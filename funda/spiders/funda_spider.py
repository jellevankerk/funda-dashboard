import re
import scrapy
from scrapy import Spider
from scrapy.linkextractors import LinkExtractor
from funda.items import FundaItem

class FundaSpider(Spider):

    name = "funda_spider"
    allowed_domains = ["funda.nl"]

    def __init__(self, place='amsterdam'):
        self.base_url = f"https://www.funda.nl/koop/{place}/"
        self.start_urls = [self.base_url]
        self.le1 = LinkExtractor(allow=r'%s+(huis|appartement)-\d{8}' % self.base_url)


    def parse(self, response):
        links = self.le1.extract_links(response)
        for link in links:
            if link.url.count('/') == 6 and link.url.endswith('/'):
                item = FundaItem()
                item['url'] = link.url
                if re.search(r'/appartement-',link.url):
                    item['property_type'] = "apartment"
                elif re.search(r'/huis-',link.url):
                    item['property_type'] = "house"
                yield scrapy.Request(link.url, callback=self.parse_dir_contents, meta={'item': item})
                
        next_page =  response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback = self.parse)

    def parse_dir_contents(self, response):
        new_item = response.request.meta['item']
        title = response.xpath('//title/text()').extract()[0]
        postal_code = re.search(r'\d{4} [A-Z]{2}', title).group(0)
        city = re.search(r'\d{4} [A-Z]{2} \w+',title).group(0).split()[2]
        address = re.findall(r'te koop: (.*) \d{4}',title)[0]
        price_dd = response.xpath('.//strong[@class="object-header__price"]/text()').extract()[0]
        price = ''.join(re.findall(r'\d+', price_dd)).replace('.','')
        year_built = self.constructionYear(response)
        area_dd = response.xpath("//dt[text()='Wonen']/following-sibling::dd[1]/span/text()").extract()[0]
        area = re.findall(r'\d+', area_dd)[0]
        bedrooms = response.xpath("//span[contains(@title,'slaapkamer')]/following-sibling::span[1]/text()").extract()[0]


        new_item['postal_code'] = postal_code
        new_item['address'] = address
        new_item['price'] = price
        new_item['year_built'] = year_built
        new_item['area'] = area
        new_item['bedrooms'] = bedrooms
        new_item['city'] = city
        yield new_item
    

    def constructionYear(self, response):
        try:
            # Some have a single bouwjaar
            singleYear = response.xpath("//dt[text()='Bouwjaar']/following-sibling::dd/span/text()").extract()
            # Some have a period
            period = response.xpath("//dt[text()='Bouwperiode']/following-sibling::dd/span/text()").extract()
            if len(singleYear) > 0:
                # Some are built before 1906 (earliest date that Funda will let you specify)
                return re.findall(r'\d{4}', singleYear[0])[0]
            elif len(period) > 0:
                return re.findall(r'$\d{4}', period[0])[0]
            else:
                return 'unknown'
        except:
            return "Failed to parse"
