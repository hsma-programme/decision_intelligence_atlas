"""Turn fetched YouTube playlist metadata into one row per talk.

Reads a JSON file written by `fetch_youtube_playlists.py` and writes a YAML
file of talks that can be used as the contents of a Quarto listing.

Long recordings covering several talks are split into one row per talk
where the description lists them:

* Timestamps that are positions in the video (e.g. `34:23 Speaker, Title`)
  become links that start the video at that talk.
* Programme times (e.g. `09:30 Speaker, Title`) are times of day rather than
  positions in the video, so their talks link to the start of the recording.
* Plain lists of talks (for playlists in `TALK_LIST_PLAYLISTS`) also link to
  the start of the recording.

Recordings with no talk details are kept as a single row.

Usage
-----
python resources/scripts/build_youtube_talks.py <videos.json> <talks.yml>
"""

from pathlib import Path
import json
import re
import sys

import yaml


# Playlists whose session recordings list their talks one per line, without
# timestamps.
TALK_LIST_PLAYLISTS = {"RPySOC 2024"}

# A line starting with a timestamp, e.g. "2:04 Title", "1:02:03 - Title" or
# "(12:30) Title".
TIMESTAMP_LINE = re.compile(
    r"^\s*[\(\[]?(?P<time>(?:\d{1,2}:)?\d{1,2}:\d{2})[\)\]]?\s*[-–—:|,.]*\s*(?P<text>.*\S)\s*$"
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


def split_talks(video, playlist_label):
    """
    Return the talks listed in a recording's description.

    Parameters
    ----------
    video : dict
        Video metadata from `fetch_youtube_playlists.py`.
    playlist_label : str
        Label of the playlist the video belongs to.

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
            (m["text"], None if programme_time else start)
            for m, start in zip(timed, to_start_times(times))
            if not NOT_TALKS.search(m["text"])
        ]

    if playlist_label in TALK_LIST_PLAYLISTS:
        return [
            (line.strip(), None)
            for line in lines
            if line.strip() and "http" not in line
        ]

    return []


def build_talks(playlists):
    """
    Build one listing item per talk from fetched playlist metadata.

    Parameters
    ----------
    playlists : list of dict
        Playlists from `fetch_youtube_playlists.py`.

    Returns
    -------
    list of dict
        Listing items with title, year, event, description, path, image
        and date. The year is taken from the playlist label if it contains
        one (e.g. "RPySOC 2025"), otherwise from the video's publish date,
        and the event is the playlist label without the year.
    """
    items = []
    for playlist in playlists:
        label_year = re.search(r"\b(19|20)\d{2}\b", playlist["label"])
        event = re.sub(r"\s*\b(19|20)\d{2}\b", "", playlist["label"]).strip()
        for video in playlist["videos"]:
            url = f"https://www.youtube.com/watch?v={video['id']}"
            shared = {
                "year": int(label_year.group(0) if label_year else video["published"][:4]),
                "event": event,
                "image": video["thumbnail"],
                "date": video["published"][:10],
            }
            talks = split_talks(video, playlist["label"])
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


def main():
    if len(sys.argv) != 3:
        sys.exit(f"Usage: {sys.argv[0]} <videos.json> <talks.yml>")
    in_file, out_file = map(Path, sys.argv[1:])

    playlists = json.loads(in_file.read_text(encoding="utf-8"))["playlists"]
    items = build_talks(playlists)
    out_file.write_text(
        yaml.safe_dump(items, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )
    print(f"Wrote {len(items)} talks to {out_file}")


if __name__ == "__main__":
    main()
