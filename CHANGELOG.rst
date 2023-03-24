Changelog
=========

1b.1.1
------
- fixed issue with minigame

1b.1.0
------
- further optimized portfolio, watchlist, and wallet ui updates
- optimized generation of etf information dialog
- optimized trade handling
- further optimized creation of technical indicator dialog
- added 8 types of scanners to trade ideas dialog
- added Inverse Cramer, Google Trends, and WallStreetBets scanners to trade ideas dialog
- optimized retrieval and parsing of scanner data

1b.0.0
------
- market, limit, and stop orders are now available
- portfolio menu now handles short positions properly
- optimized background updates of stock portfolio and crypto wallet
- optimized the creation and update of performance icons
- all portfolio and trade information is stored at close
- implemented scanner for stocks that are up the most on the day

0.12.4
------
- all technical indicators shown on the TA tab in the chart dialog are now fully customizable
- optimized performance icon updating and rendering
- misc. code cleanups and quality improvements

0.12.3
------
- fixed bug that caused crypto wallet NAV to not update
- optimized download of stock prices and information
- misc. code quality changes
- stock charting feature now uses charting module
- charting module now properly parses indicator information from UI module
- sped up app startup process
- optimized stock info dialog rendering process
- dcf module now uses yahooquery for faster info download
- misc. optimizations

0.12.2
------
- minigame now looks for files in the right locations
- minigame can now run 60fps


0.12.1
------
- misc. bug fixes and optimizations
- general code quality improvements

0.12.0
------
- stock charts are now interactive, update automatically, and are zoomable
- added support for several technical indicators to charting dialog
- stock information for the information dialog is retrieved using the yahooquery library instead of yfinance
- stock info dialog is now much faster
- technical indicators now have customizable settings
- general code quality improvements

0.11.0
------
- ui update thread now checks if the market is open and if the user is on the portfolio or wallet tab
- added dcf model tool
- made numbers in financials dialog in stock info tool look nicer
- made chart legend look nicer
- financials chart now properly shows the data that is being charted
- misc. optimizations and readability fixes

0.10.0
------
- fixed slow load times for stock and ETF information
- fixed bug that caused game to crash when downloading crypto prices
- stock information tab is now implemented and includes equity and company information,
  mutual fund holders, news, analyst recommendations, institutional holders, balance sheet
  info, and revenue/earnings history & predictions
- fixed bug that stopped stock and ETF information from clearing once a new equity was searched for
- AI model now looks for CSV file containing stock price data in the right place

0.9.0
-----
- implemented NAV label and positions table in the crypto dialog
- changed function names to snake_case
- optimized portfolio update code by removing unnecessary function calls
- added the long/short assets labels to update thread
- added 10x leverage feature to crypto wallet

0.8.9
-----
- deleted redundant "etf.csv" file

0.8.8
-----
- crypto wallet dialog now has an XML file to store data in

0.8.7
-----
- fixed bugs with portfolio asset class pie chart
- added several new components to crypto wallet dialog

0.8.6
-----
- fixed race condition bug in the stock charting feature
- turned off portfolio dialog updates when the user is not on the portfolio dialog
- asset class pie chart now updates
- fixed misc. portfolio update bug

0.8.5
-----
- Fixed misc. bugs in AI stock prediction model

0.8.4
-----
- Misc. optimizations

0.8.3
-----
- Misc. updates to prediction model data gathering script

0.8.2
-----
- Portfolio asset class pie chart now updates

0.8.1
-----
- AI model bug fixes

0.8.0
-----
- Began implementing asset info lookup for ETFs

0.7.1
-----
- Misc. prediction AI updates

0.7.0
-----
- Added stock prediction AI to project

0.6.0
-----
- refactored code to use pyside dependencies
- added pie chart for portfolio asset classes
- removed unnecessary ticker download commands
- fixed ui update bugs

0.5.0
-----
- added option to get stock data for a certain time period
- added crypto wallet tab

0.4.0
-----
- search feature now works with ETFs

0.3.0
-----
- added chart customization features
- misc. refactoring

0.2.2
-----
- portfolio table now works

0.2.1
-----
- implemented autocomplete feature for stock charting search
- fixed bug with stock gain/loss in portfolio and watchlist tables
- fixed chart titles

0.2.0
-----
- implemented search feature for stock charting
- chart title now reflects stock being charted

0.1.3
-----
- fixed bugs with watchlist and portfolio table fonts and layouts

0.1.2
-----
- moved performance icon update code into separate function
- fixed bugs with candlestick color settings and stock performance icons

0.1.1
-----
- fixed bug that caused charting code to ignore user candle color preferences

0.1.0
-----
- Implemented icon system for watchlist tickers
- misc. refactoring of main script

0.0.0
-----
Initial commit
