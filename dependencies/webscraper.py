def getOrderBook(stockName):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    import pandas as pd

    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')

    webd = webdriver.Firefox(options=options)
    webd.get('https://www.cboe.com/us/equities/market_statistics/book/'+stockName+'/?mkt=edgx')
    webd.implicitly_wait(1)

    content = []

    for element in webd.find_elements(By.TAG_NAME, 'td'):
      if len(element.text) > 0:
        content.append(element.text)



    Bids = pd.DataFrame(columns=["Shares","Price","Time"])
    Asks = pd.DataFrame(columns=["Shares","Price","Time"])

    last10 = pd.DataFrame(columns=["Price","Shares"])


    #f = open("text.txt", "r")
    #content = f.readlines()
    #print(f.read())

    data_line = 0
    count = 2

    orders_accepted = float(content[1].replace(',', ''))
    total_volume = float(content[2].replace(',', ''))

    length = len(content)


    while count<length - 1:
      count += 1

      # Get next line from file
      line = content[count]

      fullLine = count -3
      #print(line)
      #print(fullLine)
      #print(str(line) + " line "+str(fullLine))

      #clean the input
      cleanLine = line.replace(',', '').replace('\n', '')


      match (fullLine%5):
        case 0: #shares
          num = int(cleanLine)

          if(count<=length/2):
            Bids.at[data_line, "Shares"] = num

          else:
            Asks.at[data_line, "Shares"] = num

        case 1: #price
          if(count<=length/2):
            Bids.at[data_line, "Price"] = float(cleanLine)
          else:
            Asks.at[data_line, "Price"] = float(cleanLine)

        case 2: #time
          if(count<=length/2):
            Bids.at[data_line, "Time"] = cleanLine
          else:
            Asks.at[data_line, "Time"] = cleanLine


        #last 10
        case 3: #price
          last10.at[data_line, "Price"] = float(cleanLine)

        case 4: #Shares
          last10.at[data_line, "Shares"] = int(cleanLine)

          data_line+=1




    return Bids, Asks, last10, orders_accepted, total_volume

print(getOrderBook('AMZN'))