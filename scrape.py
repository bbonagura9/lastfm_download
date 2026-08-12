from typing import Optional, Tuple
import requests
import sqlite3
from requests.adapters import HTTPAdapter
from time import sleep
from urllib3.util import Retry
from os import environ

API_ROOT_URL="http://ws.audioscrobbler.com/2.0"
API_KEY=environ["LASTFM_API_KEY"]
USER=environ["LASTFM_USER"]
TIMEOUT=10

# Configure retry strategy and mount to session
retry_strategy = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    raise_on_status=False
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
sqlite_connection = sqlite3.connect("./tracks.db")


def insert_track(
    timestamp: int,
    artist: str,
    album: str,
    name: str,
) -> None:
    try:
        sqlite_connection.execute(
            """
            INSERT INTO tracks (timestamp, artist, album, name)
            VALUES (?, ?, ?, ?);
            """,
            (timestamp, artist, album, name),
        )
        sqlite_connection.commit()

    except sqlite3.IntegrityError as exc:
        raise ValueError(f"Track with timestamp {timestamp} already exists") from exc


def latest_scraped_track_timestamp() -> int:
    try:
        rows = sqlite_connection.execute("SELECT timestamp FROM tracks ORDER BY timestamp DESC LIMIT 1")
        row = next(rows)
        return row[0]
    except StopIteration:
        print("[WARNING] Latest timestamp not found, scraping everything")
        return 0
    except sqlite3.Error as exc:
        raise ValueError(f"Error getting latest timestamp: {exc}") from exc


def get_recent_tracks(page: int, limit: int=200, from_: Optional[int]=None) -> Tuple[list, int]:
    url = f"{API_ROOT_URL}/"
    params = {
        "method": "user.getRecentTracks",
        "api_key": API_KEY,
        "user": USER,
        "limit": limit,
        "page": page,
        "format": "json",
    }
    if from_:
        params["from"] = from_
    res = session.get(
        url=url,
        timeout=TIMEOUT,
        params=params,
    )
    res.raise_for_status()
    tracks = [
        {
            'artist': track['artist']['#text'],
            'name': track['name'],
            'album': track['album']['#text'],
            'timestamp': track['date']['uts'],
        }
        for track in res.json()['recenttracks']['track']
        if not track.get("@attr", {}).get("nowplaying", False)
    ]
    total_pages = int(res.json()['recenttracks']['@attr']['totalPages'])
    return tracks, total_pages


def main():
    try:
        latest_scraped_timestamp = latest_scraped_track_timestamp()
        from_ = None
        from_page = 1
        print(f"Getting page {from_page}")
        tracks, total_pages = get_recent_tracks(from_page, 200, from_)
        page = from_page
        finished = False
        while page <= total_pages:
            for track in tracks:
                if int(track["timestamp"]) <= latest_scraped_timestamp:
                    finished = True
                    break
                insert_track(**track)

            if finished:
                break

            page = page + 1
            print(f"Getting page {page}")
            tracks, total_pages = get_recent_tracks(page, 200, from_)
            sleep(1)  # To be nice with Lastfm API
    except requests.exceptions.RetryError as e:
        print("Retries exhausted:", e)
    except requests.exceptions.HTTPError as e:
        print("HTTP error response:", e)
    except requests.exceptions.JSONDecodeError as e:
        print("JSON decode error:", e)
    except requests.exceptions.RequestException as e:
        print("Other requests error:", e)
    except KeyError as e:
        print("Key error:", e)
    except Exception as e:
        print("Other exception:", e)


if __name__ == "__main__":
    main()
