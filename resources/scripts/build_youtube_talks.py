"""Turn fetched YouTube playlist metadata into one row per talk.

For each collection in `resources/recordings/collections.yml`, reads the
`videos.json` written by `fetch_youtube_playlists.py` and writes a
`talks.yml` file of talks to the collection's folder, used as the contents of
a Quarto listing on its Atlas entry. Also writes `recordings/recordings.json`,
combining the talks from every collection for the Recordings Finder.

Long recordings covering several talks are split into one row per talk
where the description lists them:

* Timestamps that are positions in the video (e.g. `34:23 Speaker, Title`)
  become links that start the video at that talk.
* Programme times (e.g. `09:30 Speaker, Title`) are times of day rather than
  positions in the video, so their talks link to the start of the recording.
* Plain lists of talks (for playlists with `talk_list: true`) also link to
  the start of the recording.

Recordings with no talk details are kept as a single row.

Usage
-----
python resources/scripts/build_youtube_talks.py
"""

from pathlib import Path
import json
import re
import sys

import yaml


CONFIG_FILE = Path("resources/recordings/collections.yml")
FINDER_FILE = Path("recordings/recordings.json")

# A line starting with a timestamp, e.g. "2:04 Title", "1:02:03 - Title",
# "(12:30) Title" or "1. (0:30) Title".
TIMESTAMP_LINE = re.compile(
    r"^\s*(?:\d+[.)]\s*)?[\(\[]?(?P<time>(?:\d{1,2}:)?\d{1,2}:\d{2})[\)\]]?\s*[-–—:|,.]*\s*(?P<text>.*\S)\s*$"
)

# Programme items that aren't talks.
NOT_TALKS = re.compile(
    r"^(break|lunch|close|closing|end|q\s*&\s*a)\b|^lightning talks$", re.IGNORECASE
)

MAX_DESCRIPTION_LENGTH = 300


def to_seconds(time):
    """
    Convert a timestamp such as "1:02:03" or "34:23" to seconds.

    Parameters
    ----------
    time : str
        Timestamp in h:mm:ss or m:ss format.

    Returns
    -------
    int
        Number of seconds.
    """
    seconds = 0
    for part in time.split(":"):
        seconds = seconds * 60 + int(part)
    return seconds


def to_start_times(times):
    """
    Convert timestamps to seconds, fixing hours written as minutes.

    Some descriptions write e.g. "01:08" for 1 hour 8 minutes. If a
    timestamp would otherwise go backwards, and reading it as hours and
    minutes makes it go forwards, it is read that way instead.

    Parameters
    ----------
    times : list of str
        Timestamps in the order they appear.

    Returns
    -------
    list of int
        Start time of each timestamp in seconds.
    """
    starts = []
    for time in times:
        start = to_seconds(time)
        if starts and start < starts[-1] and time.count(":") == 1:
            as_hours = start * 60
            if as_hours > starts[-1]:
                start = as_hours
        starts.append(start)
    return starts


def is_programme_time(times):
    """
    Return whether timestamps look like times of day rather than positions.

    Recordings start at or near 0:00, whereas a conference programme starts
    in the morning, written with a two-digit hour such as "09:30".

    Parameters
    ----------
    times : list of str
        Timestamps in the order they appear.

    Returns
    -------
    bool
        True if the first timestamp looks like a time of day.
    """
    return bool(re.fullmatch(r"(0[7-9]|1[0-2]):\d{2}", times[0]))


def clean_description(description, max_length=MAX_DESCRIPTION_LENGTH):
    """
    Shorten a description for display, removing URLs and extra whitespace.

    Parameters
    ----------
    description : str
        Full video description.
    max_length : int or None
        Maximum length, or None to keep the whole description.

    Returns
    -------
    str
        Shortened description.
    """
    text = re.sub(r"https?://\S+", "", description)
    text = re.sub(r"\s+", " ", text).strip()
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0] + "…"
    return text


def strip_urls(text):
    """
    Remove URLs, and any separator left before them, from a talk title.

    Parameters
    ----------
    text : str
        Talk title, e.g. "Talk title - Speaker - https://example.com".

    Returns
    -------
    str
        Talk title without URLs.
    """
    return re.sub(r"[\s\-–—:|,]*https?://\S+", "", text).strip()


def split_talks(video, talk_list):
    """
    Return the talks listed in a recording's description.

    Parameters
    ----------
    video : dict
        Video metadata from `fetch_youtube_playlists.py`.
    talk_list : bool
        Whether descriptions without timestamps list one talk per line.

    Returns
    -------
    list of tuple
        (talk title, start time in seconds or None) for each talk. Empty if
        the description doesn't list the talks.
    """
    lines = video["description"].splitlines()

    timed = [m for m in map(TIMESTAMP_LINE.match, lines) if m]
    if len(timed) >= 2:
        times = [m["time"] for m in timed]
        programme_time = is_programme_time(times)
        return [
            (strip_urls(m["text"]), None if programme_time else start)
            for m, start in zip(timed, to_start_times(times))
            if not NOT_TALKS.search(m["text"])
        ]

    if talk_list:
        return [
            (line.strip(), None)
            for line in lines
            if line.strip() and "http" not in line
        ]

    return []


def video_type(video, config):
    """
    Return the type of a video, from its title or its playlist's type.

    Parameters
    ----------
    video : dict
        Video metadata from `fetch_youtube_playlists.py`.
    config : dict
        The video's playlist settings from the config file. Its optional
        `types_by_title` lists patterns and types, e.g. a pattern of
        "^Showcase" with a type of "Project showcase". The first pattern
        found in the title gives the type; otherwise the playlist's `type`
        is used.

    Returns
    -------
    str
        The video's type.
    """
    for rule in config.get("types_by_title", []):
        if re.search(rule["pattern"], video["title"], re.IGNORECASE):
            return rule["type"]
    return config["type"]


def video_event(video, config, event):
    """
    Return the event of a video, from its title or its playlist's label.

    Parameters
    ----------
    video : dict
        Video metadata from `fetch_youtube_playlists.py`.
    config : dict
        The video's playlist settings from the config file. Its optional
        `events_by_title` lists patterns and events, e.g. a pattern of
        "^PHM" with an event of "Population health management", for
        playlists covering several courses or series. The first pattern
        found in the title gives the event.
    event : str
        The event from the playlist's label, used if no pattern matches.

    Returns
    -------
    str
        The video's event.
    """
    for rule in config.get("events_by_title", []):
        if re.search(rule["pattern"], video["title"], re.IGNORECASE):
            return rule["event"]
    return event


def title_from_description(video):
    """
    Use the first line of a video's description as its title.

    For playlists whose video titles are cluttered or cut short (e.g.
    "HACA2025 - Day 1 - Main Stage") but whose descriptions start with the
    talk title.

    Parameters
    ----------
    video : dict
        Video metadata from `fetch_youtube_playlists.py`.

    Returns
    -------
    dict
        The video metadata, with the first line of the description as the
        title and the rest as the description. Unchanged if the description
        is empty.
    """
    lines = video["description"].strip().splitlines()
    if not lines:
        return video
    return {
        **video,
        "title": lines[0].strip().strip('"').strip(),
        "description": "\n".join(lines[1:]),
    }


def remove_boilerplate(video, config):
    """
    Remove text repeated in every video's title or description.

    Parameters
    ----------
    video : dict
        Video metadata from `fetch_youtube_playlists.py`.
    config : dict
        The video's playlist settings from the config file. Its optional
        `remove_from_title` is a regular expression removed from the title,
        e.g. "^INSIGHT 2020: ". Its optional `remove_from_description` lists
        regular expressions; paragraphs of the description matching any of
        them are removed, e.g. an introduction to the event series.

    Returns
    -------
    dict
        The video metadata, with the matching text removed.
    """
    title = video["title"]
    if config.get("remove_from_title"):
        title = re.sub(config["remove_from_title"], "", title, flags=re.IGNORECASE).strip()

    paragraphs = re.split(r"\n\s*\n", video["description"])
    patterns = config.get("remove_from_description", [])
    description = "\n\n".join(
        paragraph
        for paragraph in paragraphs
        if not any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in patterns)
    )
    return {**video, "title": title, "description": description}


def video_source(video, config, collection):
    """
    Return who published a video, for the Recordings Finder.

    Parameters
    ----------
    video : dict
        Video metadata from `fetch_youtube_playlists.py`.
    config : dict
        The video's playlist settings from the config file. Its optional
        `source` overrides the collection's.
    collection : dict
        The video's collection settings from the config file. Its optional
        `earlier_source` (with `before`, a date, and `source`) gives the
        source of videos published before that date, e.g. for a community
        that has been renamed.

    Returns
    -------
    str
        The video's source.
    """
    if config.get("source"):
        return config["source"]
    earlier = collection.get("earlier_source")
    if earlier and video["published"][:10] < str(earlier["before"]):
        return earlier["source"]
    return collection["source"]


def build_talks(playlists, playlist_config, collection):
    """
    Build one listing item per talk from fetched playlist metadata.

    Parameters
    ----------
    playlists : list of dict
        Playlists from `fetch_youtube_playlists.py`.
    playlist_config : dict
        Each playlist's settings from the config file, keyed by label.
    collection : dict
        The collection's settings from the config file.

    Returns
    -------
    list of dict
        Listing items with title, year, event, type, description, path,
        image and date. The year is taken from the playlist label if it
        contains one (e.g. "RPySOC 2025"), otherwise from the video's publish
        date, and the event is the playlist label without the year. Items
        also have a source, and those whose description was shortened have a
        full_description, both only used by the Recordings Finder.
    """
    items = []
    for playlist in playlists:
        config = playlist_config[playlist["label"]]
        label_year = re.search(r"\b(19|20)\d{2}\b", playlist["label"])
        event = config.get("event") or re.sub(r"\s*\b(19|20)\d{2}\b", "", playlist["label"]).strip()
        for video in playlist["videos"]:
            if any(
                re.search(pattern, video["title"], re.IGNORECASE)
                for pattern in config.get("exclude_by_title", [])
            ):
                continue
            url = f"https://www.youtube.com/watch?v={video['id']}"
            shared = {
                "year": (
                    None if config.get("no_year")
                    else int(label_year.group(0) if label_year else video["published"][:4])
                ),
                "event": video_event(video, config, event),
                "type": video_type(video, config),
                "image": video["thumbnail"],
                "date": video["published"][:10],
                "source": video_source(video, config, collection),
            }
            if config.get("title_from_description"):
                video = title_from_description(video)
            video = remove_boilerplate(video, config)
            talks = split_talks(video, config.get("talk_list", False))
            if not talks:
                item = {
                    "title": video["title"],
                    "description": clean_description(video["description"]),
                    "path": url,
                    **shared,
                }
                full_description = clean_description(video["description"], max_length=None)
                if full_description != item["description"]:
                    item["full_description"] = full_description
                items.append(item)
                continue
            for title, start in talks:
                items.append({
                    "title": title,
                    "description": (
                        f"From the recording '{video['title']}', starting at {format_time(start)}."
                        if start is not None
                        else f"Part of the recording '{video['title']}' - see its description for timings."
                    ),
                    "path": url if start is None else f"{url}&t={start}s",
                    **shared,
                })
    return items


def format_time(seconds):
    """
    Format a number of seconds as h:mm:ss or m:ss.

    Parameters
    ----------
    seconds : int
        Number of seconds.

    Returns
    -------
    str
        Formatted time.
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def entry_title(folder):
    """
    Return the title of the Atlas entry in a folder.

    Parameters
    ----------
    folder : pathlib.Path
        Folder containing the entry's `index.qmd`.

    Returns
    -------
    str
        The entry's title.
    """
    text = (folder / "index.qmd").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])["title"]


def main():
    config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    recordings = []
    listed = set()
    for name, collection in config.items():
        folder = Path(collection["folder"])
        videos_file = folder / "videos.json"
        if videos_file.exists():
            playlists = json.loads(videos_file.read_text(encoding="utf-8"))["playlists"]
            playlist_config = {playlist["label"]: playlist for playlist in collection["playlists"]}
            items = build_talks(playlists, playlist_config, collection)
        else:
            # Not fetched yet, e.g. a new collection added without an API key.
            # Write an empty table so its entry still renders.
            print(f"{name}: no {videos_file} - run fetch_youtube_playlists.py to fetch its videos")
            items = []

        # The entry's table shows the shortened descriptions; full ones, and
        # sources, are only used by the Recordings Finder
        out_file = folder / "talks.yml"
        listing_items = [
            {key: value for key, value in item.items() if key not in ("full_description", "source")}
            for item in items
        ]
        out_file.write_text(
            yaml.safe_dump(listing_items, allow_unicode=True, sort_keys=False, width=1000),
            encoding="utf-8",
        )
        print(f"{name}: wrote {len(items)} talks to {out_file}")

        collection_title = entry_title(folder)
        # Events only add information if there's more than one in the collection
        show_event = len({item["event"] for item in items}) > 1
        for item in items:
            # Skip talks already listed by an earlier collection, e.g.
            # conference workshops that are also in a workshop playlist
            key = (item["path"], item["title"])
            if key in listed:
                continue
            listed.add(key)
            recordings.append({
                "title": item["title"],
                "year": item["year"],
                "date": item["date"],
                "type": item["type"],
                "source": item["source"],
                "event": item["event"] if show_event else "",
                "details": item.get("full_description", item["description"]),
                "url": item["path"],
                "collection": collection_title,
                "collection_url": f"/{folder.as_posix()}/index.html",
            })

    FINDER_FILE.write_text(
        json.dumps(recordings, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(recordings)} recordings to {FINDER_FILE}")


if __name__ == "__main__":
    main()
