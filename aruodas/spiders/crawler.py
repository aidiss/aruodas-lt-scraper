# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging
import datetime

DENY_LIST = ['dalyvio-taisykles', 'duk', 'nr1', 'nt_zemelapis', 'interjeras', 'straipsniai', 'kontaktai', r'sklypai/kaune/', 'imoniu-katalogas','informacija-perkantiems-busta', 'send-message', 'ideti-skelbima']


class CrawlerSpider(CrawlSpider):
    name = 'crawler'
    allowed_domains = ['aruodas.lt']
    start_urls = ['https://www.aruodas.lt/butai', 'https://www.aruodas.lt/']

    link_rule = Rule(LinkExtractor(allow=r'https://www.aruodas.lt/butai/puslapis/\d*?', deny=DENY_LIST), follow=True)
    parse_rule = Rule(LinkExtractor(restrict_xpaths='//h3/a'), callback='parse_item', follow=True)

    rules = (link_rule, parse_rule)

    def parse_item(self, r):
        i = {}
        # Ordered by visual appearance.
        i['href'] = r.url
        i["breadcrumb"] = [x.strip() for x in r.css('div.obj-breadcrums>div>a>span::text').extract()]
        i["header"] = r.css('h1.obj-header-text::text').extract_first().strip()
        i['datetime'] = datetime.datetime.now()
        i['summary'] = r.xpath('//*[@class="obj-summary"]/text()[2]').extract_first().strip()
        total, today = r.css(".obj-top-stats>strong::text").extract_first().split("/")
        i["views"] = {"total": total, "today": today}

        # strip is risky
        i["basket"] = r.css("span.control-number::text").extract_first()

        i["price-eur"] = r.css("span.price-eur::text").extract_first().strip()
        i["price-per"] = r.css("span.price-per::text").extract_first().strip()

        # Details
        data = [x.strip() for x in r.xpath("//dl[@class='obj-details ']/*[self::dt or self::dd]/text()").extract()]
        details = list(zip(data[::2], data[1::2]))
        details = dict(details)

        details["Ypatybės:"] = r.xpath('//*[normalize-space(text()) = "Ypatybės:"]/following-sibling::*[1]/span/text()').extract()
        details["Papildomos patalpos:"] = r.xpath('//*[normalize-space(text()) = "Papildomos patalpos:"]/following-sibling::*[1]/span/text()').extract()
        details["Apsauga:"] = r.xpath('//*[normalize-space(text()) = "Apsauga:"]/following-sibling::*[1]/span/text()').extract()
        i["details"] = details

        i['description'] = r.xpath('//div[@class="obj-comment"]').extract_first()

        # i['atstumai'] = r.xpath('//div[@class="statistic-info-row"]/*//text()').extract()

        informacija = r.css('div.obj-info-bg div dl *::text').extract()
        informacija = informacija[1::2]
        informacija = list(zip(informacija[0::2], informacija[1::2]))
        informacija = {k: v for k, v in informacija if k and v}
        i['informacija'] = informacija

        # strip is risky
        i['phone'] = r.css('div.phone>span::text').extract_first()
        i["image"] = r.css('div.obj-img>img.obj-photo-big::attr(href)').extract_first()
        i["images"] = r.css("div.obj-photos>a.link-obj-thumb::attr(href)").extract()
        return i
