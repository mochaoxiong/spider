# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from mySpider.items import MyspiderItem
import re

client=MongoClient() #本地的直接默认即可
collection=client["a51job"]["APS"]

class MyspiderPipeline(object):
    def process_item(self, item, spider):#item爬虫传过来的数据
        item["job_detail_information"]=self.prcess_job_detail_information(item["job_detail_information"])
        item["job_detail_qualification"]=self.prcess_job_detail_qualification(item["job_detail_qualification"])
        print(item) #看下传进去内容
        # 因为item可以有多个，故需要判断是否是对应类的item。注意要想导入MyspiderItem
        if isinstance(item,MyspiderItem):
            collection.insert(dict(item)) #因为用了items.py存储，其不再是一个字典
        return item

    #去除不必要的东西
    def prcess_job_detail_information(self,job_detail_information):
        #其本质是个列表,用re正则表达式处理(替换\xa0和空格)
        #re.sub(匹配的内容，替换为的内容，来源）
        job_detail_information=[re.sub(r"\xa0|\s","",i) for i in job_detail_information]
        #替换为空之后，把该空字符串的元素去掉
        job_detail_information=[i for i in job_detail_information if len(i)>0]
        return job_detail_information

    def prcess_job_detail_qualification(self,job_detail_information):
        #其本质是个列表,用re正则表达式处理(替换\xa0和空格)
        #re.sub(匹配的内容，替换为的内容，来源）
        job_detail_information=[re.sub(r"\xa0|\s","",i) for i in job_detail_information]
        #替换为空之后，把该空字符串的元素去掉
        job_detail_information=[i for i in job_detail_information if len(i)>0]
        job_detail_information=''.join(job_detail_information) ##把列表中的元素放在空串中(元素间不用任何字符隔开)
        return job_detail_information




