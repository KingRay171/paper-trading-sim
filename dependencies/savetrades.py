import os
import datetime
from bs4 import BeautifulSoup


def save(trades: list):
    """
    Parses the list of trade tuples into an XML file and saves it.
    """
    currentdir = os.getcwd()
    soup = BeautifulSoup("""<trades> </trades>""", 'xml')
    for trade in trades:
        trade_soup = BeautifulSoup(
            f"""
            <trade>
            <asset>{trade[0]}</asset>
            <transaction>{trade[1]}</transaction>
            <type>{trade[2]}</type>
            <price>{trade[3]}</price>
            <qty>{trade[4]}</qty>
            <dt>{datetime.datetime.now()}</dt>
            </trade>
            """,
            'xml'
        )
        soup.select_one('trades').append(trade_soup.select_one('trade'))
    with open(currentdir + '\\' + 'assets\\trades.xml', 'w', encoding='UTF-8') as trades_file:
        trades_file.write(str(soup))
