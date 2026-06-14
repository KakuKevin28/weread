import scrapy


class WereadApiItem(scrapy.Item):
    api_name = scrapy.Field()
    request_params = scrapy.Field()
    response_body = scrapy.Field()
    context = scrapy.Field()
