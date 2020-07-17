import pandas as pd
import requests
from bs4 import BeautifulSoup
import json


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
    categoryData = pd.read_csv('links.csv')
    for category in categoryData.iloc[:, [1, 2, 3]].values:
        print(category[0], category[1])
        baseUrl = 'https://www.koovs.com/jarvis-service/v1/product/listing/complete?href=' + \
            category[2]+'&sort=relevance&page='
        res = requests.get(baseUrl+str(1))
        # print(res.status_code)
        if res.status_code == 200:
            urls = requestData(baseUrl)
            print(len(urls))
            # exit()
