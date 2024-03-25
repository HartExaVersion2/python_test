import scrapy
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
import time
import random
import re
from testproject.constant import PRICE_DATA, COMMON, STOCK, ASSETS, METADATA, FIELDS, CONFIG
from testproject.items import ProductItem
from scrapy import Request

class RandomProxyMiddleware(HttpProxyMiddleware):
    def process_request(self, request, spider):
        proxy_list = spider.settings.get('PROXY_LIST')
        if proxy_list:
            proxy = random.choice(proxy_list)
            request.meta['proxy'] = proxy


class FixPriceSpider(scrapy.Spider):
    name = 'fix_price'
    start_urls = ['https://fix-price.com/catalog/kosmetika-i-gigiena',
                  'https://fix-price.com/catalog/novinki',
                  'https://fix-price.com/catalog/sad-i-ogorod']

    city = {'skip-city': 'true',
            'locality': '%7B%22city%22%3A%22%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3%22%2C%22cityId%22%3A55%2C%22longitude%22%3A60.597474%2C%22latitude%22%3A56.838011%2C%22prefix%22%3A%22%D0%B3%22%7D'}

    items = []

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse,
                          cookies=self.city)

    def parse(self, response):
        items = response.xpath("//div[@class='product__wrapper']//a[@class='title']/@href").getall()
        for item in items:
            url = f"https://fix-price.com{item}"
            yield Request(url=url, callback=self.parse_item,
                          cookies=self.city)

        if items:

            if '?sort=sold&page=' in response.url:
                url = response.url.split('page=')[0] + 'page=' + str(int(response.url.split('page=')[1]) + 1)
            else:
                url = response.url + '?sort=sold&page=2'

            yield Request(url=url, callback=self.parse,
                          cookies=self.city)

    def parse_item(self, response):
        item = ProductItem()
        item[FIELDS.TIMESTAMP] = int(time.time())
        item[FIELDS.URL] = response.url
        item[FIELDS.RPC] = response.url.split('/')[-1].split('-')[1]
        item[FIELDS.TITLE] = self.get_title(response)
        item[FIELDS.MARKETING_TAGS] = COMMON.FIELD_NOT_SET
        item[FIELDS.BRAND] = self.get_brand(response)
        item[FIELDS.SECTION] = self.get_section(response)
        item[FIELDS.PRICE_DATA] = self.get_price_data(response)
        item[FIELDS.STOCK] = self.get_stock(response)
        item[FIELDS.ASSETS] = self.get_assets(response)
        item[FIELDS.METADATA] = self.get_metadata(response)
        item[FIELDS.VARIANTS] = COMMON.FIELD_NOT_SET
        yield item

    def get_title(self, response):
        all_title = response.xpath('//h1[@class="title"]/text()').get().split(',')
        title_name = all_title[0]
        volume = []
        for title_word in all_title:
            for vol in COMMON.UNITS_OF_VOLUME:
                if vol.lower() in title_word:
                    volume.append(title_word)
        if volume:
            title_name += ','
            title_name += ' '.join(volume)
        return title_name


    def get_brand(self, response):
        brand = response.xpath(
            "//div[@class='properties']//span[@class='title' and text()='Бренд']/following-sibling::span[@class='value']/a/text()").get()
        return brand


    def get_section(self, response):
        breadcrumb_list = []
        for crumb in response.xpath('//div[@class="crumb"]'):
            text_list = crumb.xpath('.//a/span[@class="text"]/text()').getall()
            breadcrumb_list.extend(text_list)
        return breadcrumb_list[1:]

    def get_price_data(self, response):
        price = float(response.xpath('//meta[@itemprop="price"]/@content').get())
        text_price = response.xpath('//script[contains(text(), "specialPrice")]').get()
        text_ag_product = re.findall(r'product=(.*?).similarProducts', text_price)[0][:-3]
        price_text = re.search(f'price:(.*?)(?=(?:[^"]*"[^"]*")*[^"]*$),', text_ag_product)
        try:
            spetial_price = float(price_text.group(1).replace('"', ''))
        except:
            spetial_price = price
        if not CONFIG.FIXPRICE_CARD:
            spetial_price = price
        if spetial_price < price:
            sale = ((price - spetial_price) / spetial_price) * 100
            sale_tag = "Скидка {}%".format(sale)
        else:
            sale_tag = COMMON.FIELD_NOT_SET
        price_data = {PRICE_DATA.CURRENT: spetial_price,
                      PRICE_DATA.ORIGINAL: price,
                      PRICE_DATA.SALE_TAG: sale_tag}
        return price_data

    def get_stock(self, response):
        stock = {STOCK.IN_STOCK: True,
                 STOCK.COUNT: 0}
        return stock

    def get_assets(self, response):
        images = response.xpath('//img[@class="normal"]/@src').getall()
        assets = {
            ASSETS.MAIN_IMAGE: images[0],
            ASSETS.SET_IMAGE: images,
            ASSETS.VIEW360: COMMON.FIELD_NOT_SET,
            ASSETS.VIDEO: COMMON.FIELD_NOT_SET
        }
        return assets

    def get_metadata(self, response):
        metadata = {}
        metadata[METADATA.DESCRIPTION] = response.xpath('//meta[@property="og:description"]/@content').get()
        properties = response.xpath('//p[@class="property"]')
        for property in properties:
            title = property.xpath('.//span[@class="title"]/text()').get()
            value = property.xpath('.//span[@class="value"]')
            link_text = value.xpath('.//a/text()').get()
            plain_text = value.xpath('text()').get()
            combined_text = link_text or plain_text
            metadata[title] = combined_text
        return metadata

