from bs4 import BeautifulSoup
import os

def save_port(portfolio_assettypes, portfolio_tickers, portfolio_amts, portfolio_costbases):
    currentdir = os.getcwd()
    soup = BeautifulSoup("<portfolio> </portfolio>", "xml")
    liquidity_soup = BeautifulSoup(
        f"""
        <equity>
            <type>{portfolio_assettypes[0]}</type>
            <name>{portfolio_tickers[0]}</name>
            <amount>{portfolio_amts[0]}</amount>
        </equity>
        """,
        "xml"
    )
    soup.select_one('portfolio').append(liquidity_soup.select_one('equity'))
    for asset_type, ticker, amt, basis in zip(portfolio_assettypes[1:], portfolio_tickers[1:], portfolio_amts[1:], portfolio_costbases):
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

    with open(currentdir + '\\' + 'assets\\portfolio.xml', 'w') as trades_file:
        trades_file.write(str(soup))
