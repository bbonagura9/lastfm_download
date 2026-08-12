# lastfm_download

In a paranoid thought of Last.fm going down and losing all my data since 2004, I wrote a tiny scraper to download all the data to a local file.

## Requirements

- Python >= 3.7, <4

## Setup

Create the sqlite3 database with:

`sqlite3 tracks.db`

Then paste:

```sql
CREATE TABLE tracks (
    timestamp INTEGER NOT NULL,
    artist TEXT NOT NULL,
    album TEXT NOT NULL,
    name TEXT NOT NULL
);
CREATE INDEX idx_tracks_timestamp ON tracks (timestamp);
```

## Running

`LASTFM_API_KEY=your-api-key LASTFM_USER=your-user python3 scrape.py`
