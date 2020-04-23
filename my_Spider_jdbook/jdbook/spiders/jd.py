# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json
import urllib
import re
import time


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com','p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        dt_list=response.xpath("//div[@class='mc']/dl/dt") #大分类列表(多个dt）
        for dt in dt_list:
            item={}
            item['b_cate']=dt.xpath('./a/text()').extract_first()
            em_list=dt.xpath('./following-sibling::dd[1]/em') #兄弟节点（并行）
            for em in em_list:
                item["s_href"]=em.xpath("./a/@href").extract_first()
                item["s_cate"]=em.xpath("./a/text()").extract_first()
                if item["s_href"] is not None:
                    item["s_href"]="https:"+item["s_href"]
                    yield scrapy.Request(
                        item["s_href"],
                        callback=self.parse_book_list,
                        meta={"item":deepcopy(item)}
                    )

    def parse_book_list(self,response): #解析列表页（多本图书）
        item=response.meta["item"]
        li_list=response.xpath("//div[@id='plist']/ul/li")
        for li in li_list:
            item['book_href']=li.xpath(".//div[@class='p-img']/a/@href").extract_first()
            item['book_img']=li.xpath(".//div[@class='p-img']//img/@src").extract_first()
            if item['book_img'] is None:
                item['book_img']=li.xpath(".//div[@class='p-img']//img/@data-lazy-img").extract_first()
            item['book_img']="https:"+item['book_img'] if item['book_img'] is not None else "爬不到啊********"
            item['book_name']=li.xpath(".//div[@class='p-name']/a/em/text()").extract_first().strip() #.strip 去除头尾空格
            item['book_author']=li.xpath(".//span[@class='author_type_1']/a/text()").extract_first()
            item['book_press']=li.xpath(".//span[@class='p-bi-store']/a/@title").extract_first()
            item['book_publish_date']=li.xpath(".//span[@class='p-bi-date']/text()").extract_first().strip()
            #价格不是element响应直接给出，而是后续再请求，所以需要重新查找构造价格的url
            item["book-sku"]=li.xpath("./div/@data-sku").extract_first()
            yield scrapy.Request(
                #构造价格url
                "https://p.3.cn/prices/mgets?skuIds=J_{}".format(item["book-sku"]),
                callback=self.parse_book_price,
                meta={"item":deepcopy(item)}  #深度复制使得各个循环独立
            )
        #列表页翻页
        next_url=response.xpath("//a[@class='pn-next']/@href").extract_first()
        if next_url is not None:
            #构造完整的下一页url
            next_url=urllib.parse.urljoin(response.url,next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item':item}
            )

    def parse_book_price(self,response):
        item=response.meta['item']
        item['book_price']=json.loads(response.body.decode())[0]['op']
        book_id=re.search(r"\d+",item['book_href']).group() #书的代号
        yield scrapy.Request(
            #构造评论url
            "https://club.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=5&page=0&pageSize=10".format(book_id),
            callback=self.parse_book_comment,
            meta={"item": deepcopy(item)}
        )

    def parse_book_comment(self,response):#返回是json
        item=response.meta['item']
        json_response=json.loads(response.body.decode('gbk'))['comments']
        item["book_comment"]=[]
        for i in json_response:
            item["book_comment"].append(i['content'])
        print(item)






