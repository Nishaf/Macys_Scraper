from selenium import webdriver
from pymongo import MongoClient
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from time import sleep
import datetime

class Macys_Scraper:
    def __init__(self):
        self.urls = [
            "https://www.macys.com/shop/womens-clothing/womens-pants/Brand/Michael%20Kors%7Cadidas%7CPuma%7CReebok%7CUnder%20Armour?id=157&EFCKEY=%7B%22EXPERIMENT%22%3A%5B%222525%22%2C%222554%22%2C%222244%22%5D%7D",
        ]
        self.display = Display(visible=0, size=(1500, 800))
        #self.display.start()
        self.mongo = MongoClient()
        self.driver = webdriver.Chrome('/home/nishaf/PycharmProjects/Forever21_Scraper/chromedriver')
        self.driver.implicitly_wait(20)
        self.run()
        self.driver.close()

    def diff_dates(self, date1, date2):
        data1 = datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M:%S.%f")
        diff = date2 - data1
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        print(hours)
        return int(hours)

    def refine_links_collection(self):
        mongo = MongoClient()
        db = mongo['Macys_Scraper']
        link_col = db['pants_product_links']
        item_col = db['pants']
        item_col_links = [doc['link'] for doc in item_col.find()]

        for link in link_col.find():
            if link['url'] not in item_col_links:
                print("Not Deleting link -->  " + link['url'])
                continue
            if link['url'] in item_col_links:
                item = item_col.find_one({'link': link['url']})
                if self.diff_dates(str(item['datetime']), datetime.datetime.now()) >= 24:
                    print("Not Deleting link -->  " + link['url'])
                    continue
                else:
                    link_col.delete_one({'url': link['url']})
                    print("Deleting link -->  " + link['url'])

        mongo.close()

    def get_all_products(self):
        self.save_product_links()
        while True:
            try:
                self.driver.find_element_by_xpath("//li[@class='nextPage ']").click()
                sleep(2)
                self.save_product_links()
            except:
                break


    def save_product_links(self):
        mongo = MongoClient()
        db = mongo["Macys_Scraper"]
        soup = BeautifulSoup(self.driver.page_source)

        for item in self.driver.find_elements_by_xpath("//ul[@class='items large-block-grid-3']/li/div/div/a"):
            if db.pants_product_links.find({"url": item.get_attribute('href')}).count() ==  0:
                print(item.get_attribute('href'))
                db.pants_product_links.insert({"url": item.get_attribute('href')})
        mongo.close()

    def run(self):
        for i in self.urls:
            self.driver.get(i)
            self.get_all_products()
        self.refine_links_collection()