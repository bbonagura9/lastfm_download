from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ScrapUntilPipeline:
    def process_item(self, item, spider):
        if not spider.scrap_until:
            return item

        adapter = ItemAdapter(item)
        if adapter.get('timestamp') <= spider.scrap_until:
            raise DropItem(f"Item timestamp before limit: {adapter.get('timestamp')}")

        return item
