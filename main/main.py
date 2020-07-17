import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import threading
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')


def fetchProductDetails(soup):
    try:
        productDetails = {}
        tempDict = {}
        count = 0
        keys = soup.find('div', attrs={'class': 'tab-content'})
        # print(keys)
        for key in keys.find_all('div'):
            # print(key.text)
            try:
                productDetails[key.contents[0]] = soup.find(
                    'div', attrs={'id': 'slide-'+str(count)}).text.replace('\n', "--")
                count += 1
            except Exception as err:
                logging.error(
                    f"ERROR:fetchProductDetails::{key}", exc_info=True)
    except Exception as err:
        logging.error("ERROR:fetchProductDetails::", exc_info=True)
    return str(productDetails)


def fetchProductInfo(soup):
    tempString = ""
    try:
        productDetails = {"Product Name": "null",
                          "Product Brand": "null", "Product Sizes": "null", }
        if soup.find('div', attrs={'class': 'product-brand-name'}) is not None:
            productDetails["Product Brand"] = soup.find(
                'div', attrs={'class': 'product-brand-name'}).text

        if soup.find('div', attrs={'class': 'product-name'}) is not None:
            productDetails["Product Name"] = soup.find(
                'div', attrs={'class': 'product-name'}).text

        for i in soup.find_all('div', attrs={'class': 'size-data_round'}):
            tempString += (i.text+",")
        if tempString == "":
            tempString = "null"
        productDetails["Product Sizes"] = tempString
        tempString = ''
    except Exception as err:
        logging.error("ERROR:fetchProductInfo::", exc_info=True)
    return productDetails


def fetchPrice(soup):
    # Price Data Format: Price,MRP,Discount
    priceData = {"Price": 0, "MRP": 0, "Discount": "None"}
    try:
        if soup.find('div', attrs={'class': 'pd-discount-price'}) is not None:
            priceData["MRP"] = int(soup.find(
                'div', attrs={'class': 'pd-discount-price'}).text[2:].replace(',', ""))
            priceData["Price"] = int(soup.find(
                'span', attrs={'class': 'pd-price-striked'}).text[2:].replace(',', ""))
            priceData["Discount"] = soup.find(
                'div', attrs={'class': 'pd-discount-percent'}).text
        else:
            # print(soup.find('span', attrs={'class': 'pd-price'}).contents)
            priceData["Price"] = int(
                soup.find('span', attrs={'class': 'pd-price'}).text[2:].replace(',', ""))
    except Exception as err:
        logging.error("Error: fetchPrice:: ", exc_info=True)
    return priceData


def compileData(url, category, subCategory, productIndex):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        dataDictionary = {}
        dataDictionary['Category'] = category
        dataDictionary['Sub-Category'] = subCategory
        dataDictionary.update(fetchProductInfo(soup))
        dataDictionary.update(fetchPrice(soup))
        dataDictionary["Product Details"] = (fetchProductDetails(soup))
        lck.acquire()
        dataSet = pd.DataFrame(dataDictionary, index=[productIndex])
        dataSet.to_csv('dataset.csv', mode='a', header=False)
        lck.release()
        # print(dataDictionary)
    except Exception as err:
        logging.error("ERROR: compileData::", exc_info=True)
    return


def requestData(baseUrl):
    dataDictionary = {}
    urls = []
    res = requests.get(baseUrl+str(0))
    pageNumber = 1
    while res.status_code == 200:
        dataDictionary = json.loads(res.text)
        with open('tempdata.json', 'w') as file:
            file.write(res.text)
        for product in dataDictionary.get('data')[0].get('data'):
            urls.append('https://www.koovs.com' +
                        product.get('links')[0].get('href'))
        res = requests.get(baseUrl+str(pageNumber))
        pageNumber += 1
    return urls


if __name__ == "__main__":
    lck = threading.Lock()
    logging.info("Staring main...")
    categoryData = pd.read_csv('links.csv')
    countForProduct = 1
    for category in categoryData.iloc[:, [1, 2, 3]].values:
        logging.info("Category:"+category[0]+"/"+category[1])
        baseUrl = 'https://www.koovs.com/jarvis-service/v1/product/listing/complete?href=' + \
            category[2]+'&sort=relevance&page='
        res = requests.get(baseUrl+str(1))
        if res.status_code == 200:
            urls = requestData(baseUrl)
            logging.info(f"Length of URL: {len(urls)}")
            with ThreadPoolExecutor(max_workers=40) as executor:
                for url in urls:
                    try:
                        executor.submit(compileData, url,
                                        category[0], category[1], countForProduct)
                        countForProduct += 1
                    except Exception as err:
                        logging.error(
                            "ERROR:ThreadPoolExecutor::", exc_info=True)
