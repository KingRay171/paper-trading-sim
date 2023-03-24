
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Make request to webpage and parse html
def get_google_trends() -> pd.DataFrame:
    response = requests.get('https://www.quiverquant.com/googletrends/')
    soup = BeautifulSoup(response.text, 'html.parser')


    # Scrape the table into the list, stock_list
    result = [
        {
        'Ticker' : row.find_all('td')[0].text,
        'Trend Score' : row.find_all('td')[1].text
        }
        for row in soup.find("table", {"id": "myTable"}).find('tbody').find_all('tr')
    ]

    return pd.DataFrame(result)


def get_cramer_recs() -> pd.DataFrame:

    response = requests.get('https://www.quiverquant.com/cramertracker/')
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table in the html document
    rows = soup.find("div", {"class": "holdings-table table-inner"}).find('table').find('tbody').find_all('tr')


    # Scrape the table into the list, stock_list
    stock_list = []
    for row in rows:
        dic = {}

        # Try getting all columns
        dic['Stock'] = row.find_all('td')[0].text
        dic['Direction'] = row.find_all('td')[1].text
        dic['Date'] = row.find_all('td')[2].text
        try:
            dic['Return Since'] = row.find_all('td')[3].text
        except IndexError: # no return data
            dic['Return Since'] = "N/A"

        stock_list.append(dic)


    # Convert the list into an easily accessible Pandas dataframe

    return pd.DataFrame(stock_list)


def get_wsb_tickers() -> pd.DataFrame:
    response = requests.get('https://www.quiverquant.com/wallstreetbets/')
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table in the html document
    rows = soup.find("table", {"id": "myTable"}).find('tbody').find_all('tr')


    # Scrape the table into the list, stock_list
    stock_list = []
    for row in rows:
        dic = {}

        # Try getting all columns
        dic['Stock'] = row.find_all('td')[0].text
        dic['Mentions'] = row.find_all('td')[1].text
        dic['% Change'] = row.find_all('td')[2].text


        stock_list.append(dic)


    # Convert the list into an easily accessible Pandas dataframe

    return pd.DataFrame(stock_list)
