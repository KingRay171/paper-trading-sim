def function(string stockName):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    import pandas as pd

    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')

    webd = webdriver.Firefox(options=options)
    webd.get('https://www.cboe.com/us/equities/market_statistics/book/AMZN/?mkt=edgx')
    webd.implicitly_wait(1)
    data = {
        "Stock Name": [],
        "Shares": [],
        "Price": [],
        "Time": [],
        "Orders Accepted":[],
        "Total Volume": [],
        "Bids": [],
        "Asks": []
    }

    df = pd.DataFrame(data)

    for element in webd.find_elements(By.TAG_NAME, 'td'):
        if len(element.text) > 0:
            print(element.text)
            print(element.get_attribute('id'))

https://au.indeed.com/jobs?q=software+developer&l=Australia
