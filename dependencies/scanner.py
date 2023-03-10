import yahooquery as yq

def get_results(search_criteria, sort_field=None) -> list[dict]:
    results = []
    scan_results = yq.Screener().get_screeners(search_criteria, 100)[search_criteria]['quotes']
    for quote in scan_results:
        quote_dict = {}
        quote_dict['symbol'] = quote['symbol']
        quote_dict['name'] = quote['shortName']
        quote_dict['price'] = quote['regularMarketPrice']
        quote_dict['price_chg'] = quote['regularMarketChange']
        quote_dict['price_chg_pct'] = quote['regularMarketChangePercent']
        if sort_field:
            quote_dict[sort_field] = quote[sort_field]
        results.append(quote_dict)

    return results

