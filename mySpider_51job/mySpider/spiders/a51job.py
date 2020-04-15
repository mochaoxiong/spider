# -*- coding: utf-8 -*-
import scrapy
import logging
from mySpider.items import MyspiderItem #不用管波兰小

logger=logging.getLogger(__name__)#获取本py文件名


class A51jobSpider(scrapy.Spider):
    name = '51job'
    allowed_domains = ['51job.com'] #允许爬取的范围
    start_urls = ['https://search.51job.com/list/000000,000000,0000,00,9,99,APS,2,1.html'] #

    def parse(self, response):  #仅仅parse，不能修改
        #response为start_url地址对应的响应
        #分组
        li_list=response.xpath("//div[@class='dw_table']/div[@class='el']")
        for li in li_list:
            #item={} 用items.py取代
            item=MyspiderItem() #新建该类的对象即可
            # item["job_name"]=li.xpath("./p/span/a/@title").extract()[0] #提取后选择第一个元素
            item["job_name"]=li.xpath("./p/span/a/@title").extract_first() #提取第一个
            item["job_corp"]=li.xpath("./span[@class='t2']/a/@title").extract()[0]
            item["job_address"]=li.xpath("./span[@class='t3']/text()").extract()[0]
            item["job_salary"]=li.xpath("./span[@class='t4']/text()").extract()[0] if len(li.xpath("./span[@class='t4']/text()").extract())>0 else None
            item["job_detail_url"]=li.xpath("./p/span/a/@href").extract_first()
            #logger.warning(item)
            #yield item  #传给管道pipelines.py
            yield scrapy.Request(#由于详情页的数据还未获取加入到字典，故先不给管道
                item["job_detail_url"], #此为详情页的url
                callback=self.parse_detail,
                meta={"item":item} #键值对的键item是任意取，只为在parse_detail可以获取到
            )
        #获取总页码数
        total_urlNum=response.xpath("//input[@id='hidTotalPage']/@value").extract_first()
        #获取当前页码数
        now_urlNum = response.xpath("//input[@id='jump_page']/@value").extract_first()
        if now_urlNum!=total_urlNum:
            #找到下一页的url地址
            next_url=response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
            # 把next_url传给callback回调函数执行#可以重写其余callback解析函数
            # 这里就是构造新的request对象给引擎，引擎再给调度器
            yield scrapy.Request(
                next_url,
                callback=self.parse
            )

    def parse_detail(self,response):#处理详情页
        item=response.meta["item"]
        item["job_detail_qualification"] = response.xpath("//div[@class='cn']/p/@title").extract_first()
        item["job_detail_welfare"] = response.xpath("//div[@class='cn']/div[@class='jtag']/div/span//text()").extract()
        item["job_detail_information"] = response.xpath("//div[@class='tCompany_main']//div/p//text()").extract()
        #字典数据都加完了，可以传给pipeline
        yield item