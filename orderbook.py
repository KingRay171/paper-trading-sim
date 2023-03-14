
from selenium import webdriver
from selenium.webdriver.common.by import By


options = webdriver.FirefoxOptions()
options.add_argument('-headless')

webd = webdriver.Firefox(options=options)
webd.get('https://www.cboe.com/us/equities/market_statistics/book/AMZN/?mkt=edgx')
webd.implicitly_wait(1)
for element in webd.find_elements(By.TAG_NAME, 'td'):
    if len(element.text) > 0:
        print(element.text)
        print(element.get_attribute('id'))

