from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime



class ProductsScraper:
    def __init__(self, driver, link, item_collection):
        self.title = None
        self.driver = driver
        self.link = link
        self.item_collection = item_collection
        print(self.link)
        count = 0
        while self.title is None:
            if count >= 2:
                break
            self.driver.get(self.link)
            self.set_color_list()
            sleep(4)
            self.run_scraper()
            count += 1

    def set_color_list(self):
        self.colors = []
        self.single_color = None
        soup = BeautifulSoup(self.driver.page_source)
        try:
            colors = soup.find('div', attrs={'class': 'colorsSection'})
            ul = colors.find_all('ul', attrs={'class': 'swatchesList'})
            ul = ul[0]
            for i in ul.find_all('li'):
                self.colors.append(i.get('data-title').strip())
        except:
            self.colors = None
            self.single_color = soup.find('span', attrs={'class': 'swatchName'}).text

    def run_scraper(self):
        if self.colors is None and self.single_color is not None:
            self.store_data()
        elif self.colors is not None:
            for color in self.colors:
                elem = self.driver.find_element_by_xpath("//li[@data-title='" + str(color) + "']")
                try:
                    sleep(2)
                    elem.click()
                except:
                    try:
                        sleep(2)
                        elem.click()
                    except:
                        print("Not able to click")
                        continue
                sleep(2)
                self.store_data()

    def get_description(self, soup):
        try:
            return (soup.find('section', attrs={'class': 'product-details-content ui-accordion-content ui-helper-reset no-division'}).text).strip()
        except:
            return None

    def get_images(self, soup):
        images = list()
        try:
            images_soup = soup.find('div', attrs={'class': 'altImagesContent'})
            for image in images_soup.find_all('li'):
                img = image.get('style')
                if 'url(' in img:
                    img = img.split('url(')
                    img = img[1].split(')')
                    print(img[0])
                images.append(img[0])
            return images
        except:
            if images is not None:
                return images
            else:
                return None

    def get_sizes_and_prices(self, soup):
        size_list = list()
        try:
            sizesSection = soup.find("div", attrs={'class': 'sizesSection'})
            sizes = sizesSection.find('ul', attrs={'class': 'swatchesList'})
            for i in sizes.find_all("li"):
                size_list.append(i.text.strip())

        except:
            try:
                sizesSection = soup.find("div", attrs={'class': 'sizesSection'})
                size = sizesSection.find('span', attrs={'class': 'swatchName'})
                size_list.append((size.text).strip())
            except:
                return None, None
        try:
            price = soup.find('span', attrs={'class': 'priceSale'}).text.strip()
        except:
            price = soup.find('span', attrs={'class': 'singlePrice'}).text.strip()
        price = price.split("PKR")[1].strip() if 'PKR' in price else price
        price_list = [price for i in range(len(size_list))]

        return size_list, price_list

    def get_title(self, soup):
        try:
            title = soup.find('h1', {'class': 'productName'}).text.strip()
            brand = (soup.find('a', attrs={'class': 'brandNameLink'}).text).strip()
        except:
            title = None
            brand = None
        return title, brand


    def get_page_html(self, soup):
        try:
            page_html = soup.prettify()
        except:
            page_html = ""
        return page_html.strip()

    def get_color(self, soup):
        try:
            color_name = ((soup.find('span', attrs={'class': 'swatchName'})).text).strip()
        except:
            color_name = ""
        return color_name

    def store_data(self):
            soup = BeautifulSoup(self.driver.page_source)
            description = self.get_description(soup)
            images = self.get_images(soup)
            size_list, price_list = self.get_sizes_and_prices(soup)
            self.title, brand = self.get_title(soup)
            page_html = self.get_page_html(soup)
            color_name = self.get_color(soup)

            doc = {
                'size': size_list,
                'price': price_list,
                'tag': ['Product Type_Jackets/Coats', 'Brand_' + brand, 'Color_' + color_name],
                'link': self.driver.current_url,
                'product_type': 'jackets',
                'id': self.driver.current_url,
                'color': color_name,
                'vendor': brand,
                'description': description,
                'title': self.title,
                'images': images,
                'page_html': page_html,
                'shopify_id': '',
                'datetime': datetime.now()
            }

            if self.title is not None:
                print("TITLE: " + self.title)
                print(doc)
                self.item_collection.insert(doc)



