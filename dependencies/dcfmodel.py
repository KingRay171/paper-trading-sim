import warnings

from lxml import html
import requests
import yahooquery as yq

warnings.filterwarnings('ignore')

def parse(ticker: str) -> dict:
    """
    Retrieves and parses the relevant information (free cash flow, growth estimate if one exists,
    shares outstanding, earnings per share, and market price) for the relevant ticker for the DCF
    calculation function
    """
    yq_ticker = yq.Ticker(ticker)
    ticker_data = yq_ticker.all_modules[ticker]
    company_name = ticker_data['price']['longName']

    last_fcf = yq_ticker.cash_flow()['FreeCashFlow'].iloc[-1]

    url = f"https://finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"
    header_str = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'
    response = requests.get(url, headers={'User-Agent': header_str}, timeout=5)
    parser = html.fromstring(response.content)
    growth_est = parser.xpath('//table//tbody//tr')

    for row in growth_est:
        label = row.xpath("td/span/text()")[0]
        if 'Next 5 Years' in label:
            try:
                growth_est = float(row.xpath("td/text()")[0].replace('%', ''))
            except ValueError:
                growth_est = []
            break

    shares = ticker_data['defaultKeyStatistics']['sharesOutstanding']

    eps = ticker_data['defaultKeyStatistics']['trailingEps']

    market_price = ticker_data['price']['regularMarketPrice']
    return {
        'company_name' : company_name,
        'fcf': last_fcf,
        'ge': growth_est,
        'shares': shares,
        'eps': eps,
        'mp': market_price
    }


def get_dcf(data: dict) -> dict:
    """
    Calculates forecasted cashflows, their present values, and a fair price for the asset from a
    dictionary created by the parse method in this module
    """
    forecast = [data['fcf']]

    if data['ge'] == []:
        raise ValueError("No growth rate available from Yahoo Finance")

    for i in range(1, data['yr']):
        forecast.append(round(forecast[-1] + (data['ge'] / 100) * forecast[-1], 2))

    forecast.append(
        round(forecast[-1] * (1 + (data['pr'] / 100)) / (data['dr'] / 100 - data['pr'] / 100), 2)
    )

    discount_factors = [1 / (1 + (data['dr'] / 100))**(i + 1) for i in range(len(forecast) - 1)]

    pvs = [round(f * d, 2) for f, d in zip(forecast[:-1], discount_factors)]
    pvs.append(round(discount_factors[-1] * forecast[-1], 2)) # discounted terminal value

    result = {}

    result['forecasted_cash_flows'] = forecast

    result['cashflow_present_values'] = pvs

    dcf = sum(pvs)

    result['fair_value'] = dcf / data['shares']

    return result


def graham(data: dict) -> dict:
    """
    Calculates the Graham expected value and growth estimate from a
    dictionary created by the parse method in this module
    """
    result = {}

    if data['eps'] > 0:
        expected_value = data['eps'] * (8.5 + 2 * (data['ge']))
        ge_priced_in = (data['mp'] / data['eps'] - 8.5) / 2

        result['graham_expected_value'] = expected_value

        result['graham_growth_estimate'] = ge_priced_in

    return result


def get_fairval(ticker: str, discount_rate: float, perpetual_rate: float, growth_est: float = None, term: int = 5, eps: float = None) -> dict:
    """
    Returns both DCF and Graham valuations for the given ticker and parameters, along with
    future cashflow predictions and their present values
    """
    data = parse(ticker)
    result = data.copy()

    if growth_est is not None:
        data['ge'] = growth_est
    if eps is not None:
        data['eps'] = eps

    data['dr'] = discount_rate
    data['pr'] = perpetual_rate
    data['yr'] = term

    result.update(get_dcf(data))

    result.update(graham(data))
    return result
