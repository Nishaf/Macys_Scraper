from pymongo import MongoClient
from selenium import webdriver
from Jeans.Product_Scraper import ProductsScraper
from Jeans.Macys_Scraper import Macys_Scraper
from pyvirtualdisplay import Display


def check_all_links_visited():
    mongo = MongoClient()
    database = mongo['Macys_Scraper']
    link_collection = database['jeans_product_links']
    item_collection = database['jeans']
    item_collection_links = [doc['link'] for doc in item_collection.find()]
    for link in link_collection.find():
        if link['url'] not in item_collection_links:
            mongo.close()
            return False
    mongo.close()
    return True


if __name__ == "__main__":
    Macys_Scraper()
    while not check_all_links_visited():
        mongo = MongoClient()
        database = mongo['Macys_Scraper']
        link_collection = database['jeans_product_links']
        item_collection = database['jeans']
        display = Display(visible=0, size=(1500, 800))
        display.start()
        mongo = MongoClient()
        driver = webdriver.Chrome('/home/nishaf/PycharmProjects/Forever21_Scraper/chromedriver')
        driver.implicitly_wait(20)
        count = 0
        item_count = 1
        visited_links = [doc['link'] for doc in item_collection.find()]
        print(visited_links)
        for link in link_collection.find(no_cursor_timeout=False):
                print(len(visited_links))
                if link['url'] in visited_links:
                    print("Visited Before")
                    print("Deleting link data -->  " + link['url'])
                    item_collection.delete_many({"link": link['url']})

                scraper = ProductsScraper(driver, link['url'], item_collection)
                if scraper.title is not None:
                    print('Links opened : ' + str(item_count) + ' ---> ' + str(link))
                item_count += 1
        try:
            mongo.close()
            driver.close()
        except:
            print("Error Closing the driver")
