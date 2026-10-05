"""Fetch video metadata for YouTube playlists using the YouTube Data API.

Reads the API key from the `YOUTUBE_API_KEY` environment variable, or from a
`.env` file in the project root. For each collection in
`resources/recordings/collections.yml`, writes a `videos.json` file to the
collection's folder, containing each video's title, description, publish
date, duration and thumbnail.

Usage
-----
python resources/scripts/fetch_youtube_playlists.py [collection ...]

Fetches all collections if none are given.
"""

from pathlib import Path
import json
import os
import re
import sys
import urllib.parse
import urllib.request

import yaml


API_URL = "https://www.googleapis.com/youtube/v3/"

CONFIG_FILE = Path("resources/recordings/collections.yml")


def get_api_key():
    """
    Return the YouTube API key from the environment or a `.env` file.

    Returns
    -------
    str
        The API key.
    """
    key = os.environ.get("YOUTUBE_API_KEY")
    if key:
        return key

    env_file = Path(".env")
    if env_file.exists():
        match = re.search(
            r"^\s*YOUTUBE_API_KEY\s*=\s*[\"']?([^\s\"']+)",
            env_file.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        if match:
            return match.group(1)

    sys.exit("YOUTUBE_API_KEY not found in the environment or .env file.")


def call_api(endpoint, params, key):
    """
    Call a YouTube Data API endpoint and return the decoded JSON response.

    Parameters
    ----------
    endpoint : str
        API endpoint name, e.g. "playlistItems".
    params : dict
        Query parameters, excluding the API key.
    key : str
        The API key.

    Returns
    -------
    dict
        The decoded JSON response.
    """
    query = urllib.parse.urlencode({**params, "key": key})
    with urllib.request.urlopen(f"{API_URL}{endpoint}?{query}") as response:
        return json.load(response)


def get_playlist_video_ids(playlist_id, key):
    """
    Return the IDs of the videos in a playlist, in playlist order, without
    duplicates.

    Parameters
    ----------
    playlist_id : str
        The YouTube playlist ID.
    key : str
        The API key.

    Returns
    -------
    list of str
        Video IDs.
    """
    video_ids = []
    page_token = None
    while True:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token
        data = call_api("playlistItems", params, key)
        video_ids += [item["contentDetails"]["videoId"] for item in data["items"]]
        page_token = data.get("nextPageToken")
        if not page_token:
            # A video can appear in a playlist more than once
            return list(dict.fromkeys(video_ids))


def get_video_details(video_ids, key):
    """
    Return title, description, date, duration and thumbnail for each video.

    Private or deleted videos are not returned by the API, so are skipped.

    Parameters
    ----------
    video_ids : list of str
        Video IDs.
    key : str
        The API key.

    Returns
    -------
    list of dict
        One dictionary per available video, in the order given.
    """
    videos = []
    for start in range(0, len(video_ids), 50):
        data = call_api(
            "videos",
            {"part": "snippet,contentDetails",
             "id": ",".join(video_ids[start:start + 50])},
            key,
        )
        for item in data["items"]:
            snippet = item["snippet"]
            thumbnails = snippet.get("thumbnails", {})
            thumbnail = (thumbnails.get("medium") or thumbnails.get("default") or {}).get("url")
            videos.append({
                "id": item["id"],
                "title": snippet["title"],
                "description": snippet.get("description", ""),
                "published": snippet["publishedAt"],
                "duration": item["contentDetails"]["duration"],
                "thumbnail": thumbnail,
            })
    order = {video_id: i for i, video_id in enumerate(video_ids)}
    return sorted(videos, key=lambda video: order[video["id"]])


def main():
    config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    collections = sys.argv[1:] or list(config)
    unknown = [name for name in collections if name not in config]
    if unknown:
        sys.exit(f"Unknown collections {unknown}. Collections: {sorted(config)}")

    key = get_api_key()
    for name in collections:
        collection = config[name]
        excluded = set(collection.get("exclude_videos", [])) | {
            video_id
            for playlist_id in collection.get("exclude_playlists", [])
            for video_id in get_playlist_video_ids(playlist_id, key)
        }
        playlists = []
        for playlist in collection["playlists"]:
            # `id` may be a list, combining several playlists under one label
            playlist_ids = playlist.get("id") or []
            if isinstance(playlist_ids, str):
                playlist_ids = [playlist_ids]
            video_ids = playlist.get("videos") or [
                video_id
                for playlist_id in playlist_ids
                for video_id in get_playlist_video_ids(playlist_id, key)
            ]
            video_ids = [
                video_id
                for video_id in dict.fromkeys(video_ids)
                if video_id not in excluded
            ]
            videos = get_video_details(video_ids, key)
            playlists.append({"label": playlist["label"], "id": playlist.get("id"), "videos": videos})
            print(f"{name}: {playlist['label']}: {len(videos)} of {len(video_ids)} videos")

        out_file = Path(collection["folder"]) / "videos.json"
        out_file.write_text(
            json.dumps({"playlists": playlists}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
