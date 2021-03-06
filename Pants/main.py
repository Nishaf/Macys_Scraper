from Macys_Scraper import Macys_Scraper
from pymongo import MongoClient
from pyvirtualdisplay import Display
from selenium import webdriver
from Product_Scraper import ProductsScraper


def check_all_links_visited():
    mongo = MongoClient()
    database = mongo['checking']
    link_collection = database['pants_product_links']
    item_collection = database['pants']
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
        database = mongo['checking']
        link_collection = database['pants_product_links']
        item_collection = database['pants']
        display = Display(visible=0, size=(1500, 800))
        display.start()
        mongo = MongoClient()
        driver = webdriver.Chrome()
        driver.implicitly_wait(20)
        count = 0
        item_count = 1
        visited_links = [doc['link'] for doc in item_collection.find()]
        print(visited_links)
        for link in link_collection.find(no_cursor_timeout=False):
            try:
                print(len(visited_links))
                if link['url'] in visited_links:
                    print("Visited Before")
                    print("Deleting link data -->  " + link['url'])
                    item_collection.delete_many({"link": link['url']})

                scraper = ProductsScraper(driver, link['url'], item_collection)
                if scraper.title is not None:
                    print('Links opened : ' + str(item_count) + ' ---> ' + str(link))
                item_count += 1
            except:
                continue

        try:
            mongo.close()
            driver.close()
        except:
            print("Error Closing the driver")
