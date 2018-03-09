# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ConstructionItem(Item):
    category = Field()
    company = Field()
    address = Field()
    geo_coordinates = Field()
    number_of_reviews = Field()
    website = Field()
    email = Field()
    profile_url = Field()
    phone_number = Field()
    fax_number = Field()
