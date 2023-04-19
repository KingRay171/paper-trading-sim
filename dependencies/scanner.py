import yahooquery as yq

def get_results(search_criteria, sort_field=None) -> list[dict]:
    """
    Retrieves search results for the given criteria and parses it into a list of dictionaries,
    each with the symbol's name, ticker, price, price change in $ and %, and value for the given
    sort field if applicable.
    """

    scan_results = yq.Screener().get_screeners(search_criteria, 100)[search_criteria]['quotes']

    if sort_field:
        return [
            {
                'symbol' : quote['symbol'],
                'name' : quote['shortName'],
                'price' : quote['regularMarketPrice'],
                'price_chg': quote['regularMarketChange'],
                'price_chg_pct' : quote['regularMarketChangePercent'],
                sort_field : quote[sort_field]
            } for quote in scan_results
        ]
    else:
        return [
            {
                'symbol' : quote['symbol'],
                'name' : quote['shortName'],
                'price' : quote['regularMarketPrice'],
                'price_chg': quote['regularMarketChange'],
                'price_chg_pct' : quote['regularMarketChangePercent']
            } for quote in scan_results
        ]
