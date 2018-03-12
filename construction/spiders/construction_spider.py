# -*- coding: utf-8 -*-
import scrapy
import re

from ..items import ConstructionItem


class ConstructionSpider(scrapy.Spider):
    name = 'construction_spider'
    allowed_domains = ['construction.co.uk']
    start_urls = ['http://www.construction.co.uk/construction_directory.aspx']

    def parse(self, response):

        # GETTING SELECTOR LIST OF CATEGORIES
        categories = response.xpath("//div[@class='innerContainer']//div[@class='halfWidth padBot']")

        for category in categories:
            category_url = category.xpath("./a/@href").extract_first()
            category_name = category.xpath("./a/text()").extract_first()
            yield scrapy.Request(url=category_url,
                                 callback=self.parse_category_items,
                                 dont_filter=True,
                                 meta={'category_name': category_name})

    def parse_category_items(self, response):

        # LIST OF ALL COMPANIES
        company_list = response.xpath("//div[@id='companyList']//div[@class='defaultList fullWidth pad1']")

        # GETTING NAME OF CATEGORY
        category = str(response.xpath("//div[@class='defaulttitle_generic']/h1/text()").extract_first()).strip()

        for company in company_list:
            company_url = company.xpath("./div[@class='defaultListInfo']/a/@href").extract_first()
            yield scrapy.Request(url=company_url,
                                 callback=self.parse_company_profile,
                                 dont_filter=True,
                                 meta={'category_name': category})

        # PAGINATION
        next_page = response.xpath("//div[@class='nextLink']/a/@href").extract_first()
        if next_page:
            yield scrapy.Request(url=next_page,
                                 callback=self.parse_category_items,
                                 dont_filter=True)

    def parse_company_profile(self, response):

        item = ConstructionItem()

        # Getting structure of main container
        main_container = response.xpath("//div[@class='mainContainer']/div[@itemscope='itemscope']")

        # CATEGORY
        item['category'] = response.meta['category_name']

        # COMPANY
        item['company'] = main_container.xpath("//div[@class='listingContactDetailsTitle']/h2/span/text()").extract_first()

        # ADDRESS

        # Getting structure of address container
        address_container = response.xpath("//div[@class='compAddress']/div[@itemprop='address']")

        item['address'] = {
            'street': ', '.join(address_container.xpath("./div[@itemprop='streetAddress']//text()").extract()),
            'city': address_container.xpath("./div[@itemprop='addressLocality']/text()").extract_first(),
            'prefecture': address_container.xpath("./div[@itemprop='addressRegion']/text()").extract_first(),
            'postal_code': address_container.xpath("./div[@itemprop='postalCode']/text()").extract_first()
        }

        # GEO
        geo_content = main_container.xpath("//div[@class='compMap']/a/img/@src").extract_first()
        item['geo_coordinates'] = geo_content.split("center=")[1].split('&')[0] if geo_content else None

        # REVIEWS
        item['number_of_reviews'] = main_container.xpath("//div[@class='overallReviews']/text()").re_first("(\d)")

        # WEBSITE
        item['website'] = main_container.xpath(
            "//div[@class='compInfo']//div[@class='compInfoDetail' and @itemprop='url']/a/@href"
        ).extract_first()

        # EMAIL
        script_content = main_container.xpath("//div[@class='compInfoDetail']/script/text()").extract_first()
        if script_content:
            char_indexes = [ord(symb) for symb in str(script_content).split("emrp('")[1].split("'")[0]]
            item['email'] = ''.join([chr(index-1) for index in char_indexes])
        else:
            item['email'] = None

        # PROFILE URL
        item['profile_url'] = response.url

        # PHONE NUMBER
        item['phone_number'] = main_container.xpath("//div[@class='compInfoDetail compTels']/div[@id='hMob']/@onclick |"
                                                    "//div[@class='compInfoDetail compTels']/div[@id='mTel']/@onclick")\
            .re_first("((\d+\s?)+)")

        # FAX NUMBER
        item['fax_number'] = main_container.xpath(
            "//div[@class='compInfoTitle' and contains(text(), 'Fax')]"
            "/following-sibling::div[@class='compInfoDetail']/text()").re_first("((\d+\s?)+\d)")

        yield item