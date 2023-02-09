# Crypto quiverquant tracker. Stocks from the last 24 hours is provided by quiverquant.
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Make request to webpage and parse html
url = 'https://www.quiverquant.com/googletrends/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table in the html document
rows = soup.find("table", {"id": "myTable"}).find('tbody').find_all('tr')


# Scrape the table into the list, stock_list
stock_list = []
for row in rows:
    dic = {}

    # Try getting all columns
    dic['Ticker'] = row.find_all('td')[0].text
    dic['Trend Score'] = row.find_all('td')[1].text

    stock_list.append(dic)


# Convert the list into an easily accessible Pandas dataframe
df = pd.DataFrame(stock_list)

print(df)
