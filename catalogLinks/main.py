import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

if __name__ == "__main__":
    res = requests.get("https://www.koovs.com/")
    soup = BeautifulSoup(res.text)
    dataList = []
    for category in soup.find_all('li', attrs={'class': 'koovs-header brand-menu__item'}):
        for list in category.find_all('li'):
            dataList.append([category.a.get('title'), (list.a.text), ('https://www.koovs.com' +
                                                                      list.a.get('href')).replace('/', '%2F').replace(':', '%3A')])
    data = pd.DataFrame(dataList)
    data.to_csv('links.csv')
