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


def clean_description(description):
    """
    Shorten a description for display, removing URLs and extra whitespace.

    Parameters
    ----------
    description : str
        Full video description.

    Returns
    -------
    str
        Shortened description.
    """
    text = re.sub(r"https?://\S+", "", description)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_DESCRIPTION_LENGTH:
        text = text[:MAX_DESCRIPTION_LENGTH].rsplit(" ", 1)[0] + "…"
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


def build_talks(playlists, playlist_config):
    """
    Build one listing item per talk from fetched playlist metadata.

    Parameters
    ----------
    playlists : list of dict
        Playlists from `fetch_youtube_playlists.py`.
    playlist_config : dict
        Each playlist's settings from the config file, keyed by playlist ID.

    Returns
    -------
    list of dict
        Listing items with title, year, event, type, description, path,
        image and date. The year is taken from the playlist label if it
        contains one (e.g. "RPySOC 2025"), otherwise from the video's publish
        date, and the event is the playlist label without the year.
    """
    items = []
    for playlist in playlists:
        config = playlist_config[playlist["id"]]
        label_year = re.search(r"\b(19|20)\d{2}\b", playlist["label"])
        event = re.sub(r"\s*\b(19|20)\d{2}\b", "", playlist["label"]).strip()
        for video in playlist["videos"]:
            url = f"https://www.youtube.com/watch?v={video['id']}"
            shared = {
                "year": (
                    None if config.get("no_year")
                    else int(label_year.group(0) if label_year else video["published"][:4])
                ),
                "event": event,
                "type": config["type"],
                "image": video["thumbnail"],
                "date": video["published"][:10],
            }
            talks = split_talks(video, config.get("talk_list", False))
            if not talks:
                items.append({
                    "title": video["title"],
                    "description": clean_description(video["description"]),
                    "path": url,
                    **shared,
                })
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
    for name, collection in config.items():
        folder = Path(collection["folder"])
        playlists = json.loads((folder / "videos.json").read_text(encoding="utf-8"))["playlists"]
        playlist_config = {playlist["id"]: playlist for playlist in collection["playlists"]}
        items = build_talks(playlists, playlist_config)

        out_file = folder / "talks.yml"
        out_file.write_text(
            yaml.safe_dump(items, allow_unicode=True, sort_keys=False, width=1000),
            encoding="utf-8",
        )
        print(f"{name}: wrote {len(items)} talks to {out_file}")

        collection_title = entry_title(folder)
        for item in items:
            recordings.append({
                "title": item["title"],
                "year": item["year"],
                "date": item["date"],
                "type": item["type"],
                "source": collection["source"],
                "event": item["event"] if len(collection["playlists"]) > 1 else "",
                "details": item["description"],
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
