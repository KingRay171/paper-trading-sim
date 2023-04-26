
def getOrderBook(stockName):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    import pandas as pd

    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')

    webd = webdriver.Firefox(options=options)
    webd.get('https://www.cboe.com/us/equities/market_statistics/book/'+stockName+'/?mkt=edgx')
    webd.implicitly_wait(1)
  
    Bids = pd.DataFrame(columns=["Shares","Price","Time"])
    Asks = pd.DataFrame(columns=["Shares","Price","Time"])

    last10 = pd.DataFrame(columns=["Price","Shares"])

    content = webd.find_elements(By.TAG_NAME, 'td')

    #f = open("text.txt", "r")
    #content = f.readlines()
    #print(f.read())

    data_line = 0
    count = 4

    orders_accepted = float(content[2].replace(',', ''))
    total_volume = float(content[4].replace(',', ''))

    length = len(content)
    
    while True:
      count += 2
   
      # if line is empty
      # end of file is reached
      if count>=length:
          break
        
      if(count%2==0):
        # Get next line from file
        line = content[count]
      
        fullLine = count/2 -3
        #print(str(line) + " line "+str(fullLine))

        #clean the input
        cleanLine = line.replace(',', '').replace('\n', '')
        

        match (fullLine%5):
          case 0: #shares 
            num = int(cleanLine)
            
            if(count<length/2):
              Bids.loc[data_line, "Shares"] = num
             
            else:
              Asks.loc[data_line, "Shares"] = num
              
          case 1: #price
            if(count<length/2):
              Bids.loc[data_line, "Price"] = float(cleanLine)
            else:
              Asks.loc[data_line, "Price"] = float(cleanLine)
              
          case 2: #time
            if(count<length/2):
              Bids.loc[data_line, "Time"] = cleanLine
            else:
              Asks.loc[data_line, "Time"] = cleanLine

        
          #last 10
          case 3: #price
            last10.loc[data_line, "Price"] = float(cleanLine)

          case 4: #Shares
            last10.loc[data_line, "Shares"] = int(cleanLine)
            
            data_line+=1
        

    

    return Bids, Asks, last10, orders_accepted, total_volume
      
