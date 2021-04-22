# lastfm_download

In a paranoid thought of Last.fm going down and losing all my data since 2004, I wrote a tiny scraper to download all the data to a local file.

## Requirements

- Python >= 3.7, <4

## Installing

Create your virtualenv and then:

```
git clone https://github.com/bbonagura9/lastfm_download.git
cd lastfm_download
poetry install
```

## Running

`scrapy crawl lastfm -a username=<your-lastfm-username>`
