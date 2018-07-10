# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class CrawlerSpider(CrawlSpider):
    name = 'crawler'
    allowed_domains = ['aruodas.lt']
    start_urls = [
        'https://www.aruodas.lt/butai',
        'https://www.aruodas.lt/']

    rules = (
        Rule(
            LinkExtractor(
                allow=r'https://www.aruodas.lt/butai/puslapis/\d*?',
                deny=['dalyvio-taisykles', 'duk', 'nr1',
                      'nt_zemelapis', 'interjeras', 'straipsniai', 'kontaktai',
                      r'sklypai/kaune/', 'imoniu-katalogas',
                      'informacija-perkantiems-busta', 'send-message', 'ideti-skelbima']),
            follow=True),
        Rule(
            LinkExtractor(
                restrict_xpaths='//h3/a'),
            callback='parse_item',
            follow=True),
    )


    def parse_item(self, response: scrapy.http.Response):
        i = {}

        i['href'] = response.url


        r = response.css('dl.obj-details ::text').extract()
        [x.strip() for x in r]
        r = [x.strip() for x in r]
        r = list(zip(r[1::5], r[3::5]))
        r = [x for x in r if x[0] and x[1]]
        r = dict(r)
        i['info'] = r

        i['comment'] = response.xpath('//p[@class="obj-comment"]//text()').extract()

        i['atstumai'] = response.xpath('//div[@class="statistic-info-row"]/*//text()').extract()

        i['summary'] = response.xpath('//*[@class="obj-summary"]/b/text()').extract()

        informacija = response.css('div.obj-info-bg div dl *::text').extract()
        informacija = informacija[1::2]
        informacija = dict(zip(informacija[0::2], informacija[1::2]))
        i['informacija'] = informacija

        i['phone'] = response.css('div.phone.small::text').extract_first().strip()

        return i
