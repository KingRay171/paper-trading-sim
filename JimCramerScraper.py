# Scrapes https://www.quiverquant.com/cramertracker/ for the table of Jim Cramer's recent stock picks.

# Imports
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Make request to webpage and parse html
url = 'https://www.quiverquant.com/cramertracker/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table in the html document
rows = soup.find("div", {"class": "holdings-table table-inner"}).find('table').find('tbody').find_all('tr')


# Scrape the table into the list, stock_list
stock_list = []
for row in rows:
    dic = {}

    # Try getting all columns
    try:
        dic['Stock'] = row.find_all('td')[0].text
        dic['Direction'] = row.find_all('td')[1].text
        dic['Date'] = row.find_all('td')[2].text
        dic['Return Since'] = row.find_all('td')[3].text
    except:
        dic['Stock'] = row.find_all('td')[0].text
        dic['Direction'] = row.find_all('td')[1].text
        dic['Date'] = row.find_all('td')[2].text
        dic['Return Since'] = 'N/A'

    stock_list.append(dic)


# Convert the list into an easily accessible Pandas dataframe
df = pd.DataFrame(stock_list)

print(df)
