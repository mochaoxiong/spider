# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job_name=scrapy.Field()
    job_corp=scrapy.Field()
    job_address=scrapy.Field()
    job_salary=scrapy.Field()
    job_detail_url=scrapy.Field()
    job_detail_qualification=scrapy.Field()
    job_detail_welfare=scrapy.Field()
    job_detail_information=scrapy.Field()

