import os
from bs4 import BeautifulSoup


def save_port(asset_types: list, tickers: list, amts: list, cost_bases: list):
    """
    Parses the given lists of portfolio tickers, asset types, amounts, and cost bases
    into an XML file and saves it to the assets directory
    """
    currentdir = os.getcwd()
    soup = BeautifulSoup("<portfolio> </portfolio>", "xml")
    liquidity_soup = BeautifulSoup(
        f"""
        <equity>
            <type>{asset_types[0]}</type>
            <name>{tickers[0]}</name>
            <amount>{amts[0]}</amount>
        </equity>
        """,
        "xml"
    )
    soup.select_one('portfolio').append(liquidity_soup.select_one('equity'))
    zip_obj = zip(asset_types[1:], tickers[1:], amts[1:], cost_bases[1:])
    for asset_type, ticker, amt, basis in zip_obj:
        soup2 = BeautifulSoup(
            f"""
            <equity>
                <type>{asset_type}</type>
                <name>{ticker}</name>
                <amount>{amt}</amount>
                <costbasis>{basis}</costbasis>
            </equity>
            """,
            "xml"
        )
        soup.select_one('portfolio').append(soup2.select_one('equity'))

    with open(currentdir + '\\' + 'assets\\portfolio.xml', 'w', encoding='UTF-8') as trades_file:
        trades_file.write(str(soup))
