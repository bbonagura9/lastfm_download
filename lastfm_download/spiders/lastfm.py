import scrapy

from lastfm_download.items import Scrobble, ScrobbleLoader


class LastfmSpider(scrapy.Spider):
    name = 'lastfm'
    allowed_domains = ['last.fm']

    def __init__(self, username, start_page=1, *args, **kwargs):
        super(LastfmSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.start_page = start_page

    def build_request(self, page):
        return scrapy.Request(
            f'https://www.last.fm/user/{self.username}/library?page={page}',
            self.parse,
            meta=dict(page=page),
        )

    def start_requests(self):
        yield self.build_request(self.start_page)

    def parse(self, response):
        page = response.meta['page']
        self.logger.info(f'Parsing page number {page}')
        for row in response.css('.chartlist-row'):
            loader = ScrobbleLoader(Scrobble(), row)
            loader.add_css('track', 'td.chartlist-name > a::attr(title)')
            loader.add_css('artist', 'td.chartlist-artist > a::attr(title)')
            loader.add_css('timestamp', 'td.chartlist-timestamp > span::attr(title)')
            # Scrobbles prior to this date come without a timestamp
            # so as a workaround, the timestamp gets a default value
            loader.add_value('timestamp', 'Monday 21 Feb 2005, 11:59pm')
            yield loader.load_item()
        yield self.build_request(page + 1)
