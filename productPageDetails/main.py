import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import threading


def fetchProductDetails(soup):
    productDetails = {}
    tempDict = {}
    count = 0
    keys = soup.find('div', attrs={'class': 'tab-content'})
    # print(keys)
    for key in keys.find_all('div'):
        # print(key.text)
        productDetails[key.text] = soup.find(
            'div', attrs={'id': 'slide-'+str(count)}).text.replace('\n', "--")
        count += 1
    return productDetails


def fetchProductInfo(soup):
    tempString = ""
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
    tempString = ""
    return productDetails


def fetchPrice(soup):
    # Price Data Format: Price,MRP,Discount
    priceData = {"Price": 0, "MRP": 0, "Discount": "None"}
    try:
        if soup.find('div', attrs={'class': 'pd-discount-price'}) is not None:
            # print(soup.find('div', attrs={'class': 'pd-discount-price'}).text)
            # print(soup.find('span', attrs={'class': 'pd-price-striked'}).text)
            # print(soup.find('div', attrs={'class': 'pd-discount-percent'}).text)
            priceData["MRP"] = int(soup.find(
                'div', attrs={'class': 'pd-discount-price'}).text[2:])
            priceData["Price"] = int(soup.find(
                'span', attrs={'class': 'pd-price-striked'}).text[2:])
            priceData["Discount"] = soup.find(
                'div', attrs={'class': 'pd-discount-percent'}).text
        else:
            # print(soup.find('span', attrs={'class': 'pd-price'}).contents)
            priceData["Price"] = int(
                soup.find('span', attrs={'class': 'pd-price'}).text[2:])
    except Exception as err:
        logging.error("Error: fetchPrice() ")
        logging.error(err)
    return priceData


def compileData(soup, category, subCategory):
    dataDictionary = {}
    dataDictionary['Category'] = category
    dataDictionary['Sub-Category'] = subCategory
    dataDictionary.update(fetchProductInfo(soup))
    dataDictionary.update(fetchPrice(soup))
    dataDictionary.update(fetchProductDetails(soup))
    lck.acquire()
    dataSet = pd.DataFrame(dataDictionary, index=[0])
    dataSet.to_csv('dataset.csv', mode='a', header=False)
    lck.release()
    print(dataDictionary)


if __name__ == "__main__":
    lck = threading.Lock()
    res = requests.get(
        "https://www.koovs.com/lazy-panda-tropical-pineapple-print-causal-shirt-131950-147982.html")
    soup = BeautifulSoup(res.text, "html.parser")
    # fetchPrice(soup)
    # fetchProductDetails(soup)
    # fetchProductInfo(soup)
    compileData(soup, "xyz", 'asasas')
