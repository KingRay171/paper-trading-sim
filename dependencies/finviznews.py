from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

def get_finviz_news(ticker: str) -> list:

    news = []
    url = f'https://finviz.com/quote.ashx?t={ticker.upper()}'
    req = Request(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
    response = urlopen(req)
    # Read the contents of the file into 'html'
    html = BeautifulSoup(response, features='lxml')
    # Find 'news-table' in the Soup and load it into 'news_table'
    table = html.find(id='news-table')
    # Add the table to our dictionary


    # Read one single day of headlines for ‘AMZN’
    # Get all the table rows tagged in HTML with <tr> into ‘amzn_tr’
    table_tr = table.findAll('tr')
    href = [link.get('href') for link in table.findAll('a')]

    date = table_tr[0].td.text.split(' ')[0]
    num_skips = 0
    for i, table_row in enumerate(table_tr):
        if table_row.span.text != "Loading…":
            current_item = {}
            source = table_row.span.text
            current_item['source'] = source
            # Read the text of the element ‘a’ into ‘link_text’
            a_text = table_row.a.text
            current_item['title'] = a_text
            # Read the text of the element ‘td’ into ‘data_text’
            td_text = table_row.td.text
            if len(td_text) == 7:
                current_item['dateTime'] = date + " " + td_text
            else:
                date = table_tr[i].td.text.split(' ')[0]
                current_item['dateTime'] = td_text
            # Print the contents of ‘link_text’ and ‘data_text’
            href_text = href[i - num_skips]
            current_item['link'] = href_text
            # Exit after printing 4 rows of data
            news.append(current_item)
            if len(news) == 10:
                return news
        else:
            num_skips += 1
