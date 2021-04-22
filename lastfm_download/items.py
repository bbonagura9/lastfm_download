# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import datetime

import scrapy
from itemloaders.processors import Compose, TakeFirst
from scrapy.loader import ItemLoader


def parse_timestamp(ts):
    return datetime.strptime(ts, "%A %d %b %Y, %I:%M%p")


class ScrobbleLoader(ItemLoader):
    default_output_processor = TakeFirst()
    timestamp_in = Compose(TakeFirst(), parse_timestamp)


class Scrobble(scrapy.Item):
    artist = scrapy.Field()
    track = scrapy.Field()
    timestamp = scrapy.Field()
