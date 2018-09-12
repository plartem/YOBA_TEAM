import scrapy
import datetime

'''
    Scraper for used cars from 'http://autoportal.ua/'

    @author Maxim G.
    @date 13.09.2018
'''

class AutoPortalSpider(scrapy.Spider):
    name = "autoportal"

    start_urls = [
        'http://sale.autoportal.ua/filters.html?vehicle_id=1',  #passenger cars
        'http://sale.autoportal.ua/filters.html?vehicle_id=5'   #minibuses
    ]

    lastUpdate = datetime.datetime(1, 1, 1)

    def parse(self, response):
        for advr in response.css('div.ads_fltr-hot').extend(response.css('div.ads_fltr')):
            updateDate = AutoPortalSpider.txt2date(advr.css('p.br05::text').extract_first())
            
            href = advr.css('a.vrtcl_itm').extract_first()
            if (href and updateDate > self.lastUpdate):
                yield response.follow(href, self.parse_advr)#change response -> advr ?????????????
    
        for next_page in response.css('a.pnext'):
            yield response.follow(next_page, callback=self.parse)

        with open('filename.json', 'wb') as f:
            f.write(response.body)

    def parse_advr(self, response):
        url = response.request.url

        block_data = response.css('div."ad_bit2 cell6"')
        updateTime = AutoPortalSpider.txt2date(block_data.css('ad_bit2_height i::text')[0])
        li_rows = block_data.css('ul.twoCol_dot li')
        fullname = li_rows[0].css('span::attr(title)')[0]
        
        brand = AutoPortalSpider.getBrand(response)
        model = AutoPortalSpider.getModel(fullname, brand)

        def getliText(index):
            return li_rows[index].css('b::text') 

        price = getliText(0)
        year = getliText(1)
        mileage = getliText(2)
        engine_capacity = getliText(3)
        fuel = getliText(4)
        #carcase -- 5
        transmission = getliText(6)
        drive = AutoPortalSpider.txt2drive(getliText(7))
        #color -- 8
        
        photos = response.css('div.preview img::attr(src)').extract()
        additionalInfo = block_data.css('div.factor bg_f1').extract_first() #NoSQL

        yield {
            "url": url,
            "updateTime" : updateTime,

            "state": 0, # 0 - used, 1 - new     Is it really need?
            "name" : {
                "full": fullname, 
                "brand": brand, 
                "model": model
            },
            "year": year,
            "mileage": mileage,
            "price": price,

            "fuel": fuel,
            "transmission": transmission,
            "drive": drive, # 0 - undefined, 1 - four-wheel, 2 - rear, 3 - front-wheel
            "engine_capacity": engine_capacity,

            "photos": photos,
            "additional": additionalInfo
        }

    @staticmethod
    def txt2date(txt):
        return datetime.datetime.now()

    @staticmethod
    def getBrand(response):
        # Get penult bread from breadcrumbs
        breadLine = response.xpath('//div[@id=breadcrumbs]/div/a/span/text()')[-2]
        # Split first unless word ['Продажа', 'Микроавтобусы']
        txt = breadLine.split(' ', 1)
        # Remaining would be brand of car
        return txt[1]

    @staticmethod
    def getModel(fullname, brand):
        # Only cut brand from fullname and add deffault value for safety
        array = fullname.split(brand, 1)
        if (len(array) > 1):
            return array[1].strip()
        else:
            pass

    @staticmethod
    def txt2drive(key):
        driveDict = {
            'Полный': 1,
            'Задний': 2,
            'Передний': 3
        }
        return driveDict.get(key, 0) 