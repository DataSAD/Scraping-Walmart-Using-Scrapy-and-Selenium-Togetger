import scrapy
from time import sleep
import undetected_chromedriver as uc
from scrapy.selector import Selector
from ..items import FoodItem

class FoodspiderSpider(scrapy.Spider):
    name = "foodspider"
    allowed_domains = ["walmart.com"]
    start_urls = ["https://www.walmart.com/browse/976759?athcpid=7cbe8a0a-c5fe-4839-a851-edb3ec71638c&athpgid=AthenaContentPage&athznid=athenaModuleZone&athmtid=AthenaItemCarousel&athtvid=4&athena=true&page=1&affinityOverride=default"]

    def __init__(self):
        self.next_page_no = 1
        with open('control.txt', 'w') as t:
            pass

    def parse(self, response):
        while True:
            driver = uc.Chrome(enable_cdp_events=True)
            driver.implicitly_wait(15)
            driver.maximize_window()
            driver.get(response.url)

            sleep(3)

            for _ in range(3):

                page_height = driver.execute_script('return document.body.scrollHeight')
                driver.execute_script(f'window.scrollTo(0, {page_height});')
                sleep(2)

            sleep(5)

            page = driver.page_source
            driver.quit()

            my_response = Selector(text=page)

            food_items = my_response.css('div[data-testid="list-view"]')

            if len(food_items) < 50:
                with open('control.txt', 'a') as t:
                    t.write(f'{len(food_items)} item for page {self.next_page_no} \n')
                    t.write('less than 50, trying again \n')
                continue
            else:
                with open('control.txt', 'a') as t:
                    t.write(f'{len(food_items)} items for page {self.next_page_no} \n')
                    t.write('OK. Scraping starting for this page \n')

            for item in food_items:
                food_item = FoodItem()

                if item.xpath('.//div[2]/span/span/text()').get() is not None:
                    food_item['name'] = item.xpath('.//div[2]/span/span/text()').get()
                else:
                    food_item['name'] = 'No Info'

                if item.xpath('.//div[2]/div/div/span[2]/text()').get() is not None:
                    food_item['price'] = (item.xpath('.//div[2]/div/div/span[2]/text()').get()
                                        + item.xpath('.//div[2]/div/div/span[3]/text()').get() + '.'
                                         + item.xpath('.//div[2]/div/div/span[4]/text()').get())
                else:
                    food_item['price'] = 'No Info'

                if item.css('img[data-testid = "productTileImage"]').attrib['src'] is not None:
                    food_item['image_link'] = item.css('img[data-testid = "productTileImage"]').attrib['src']
                else:
                    food_item['image_link'] = 'No Info'

                yield food_item

            self.next_page_no += 1

            next_page_link = f'https://www.walmart.com/browse/976759?athcpid=7cbe8a0a-c5fe-4839-a851-edb3ec71638c&athpgid=AthenaContentPage&athznid=athenaModuleZone&athmtid=AthenaItemCarousel&athtvid=4&athena=true&page={self.next_page_no}&affinityOverride=default'

            if self.next_page_no <= 25:
                yield response.follow(next_page_link, callback=self.parse)
            break










































