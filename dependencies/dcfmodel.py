from lxml import html
import requests
import yfinance as yf
import math
import warnings
warnings.filterwarnings('ignore')

def parse(ticker: str) -> dict:
    yf_ticker = yf.Ticker(ticker)

    company_name = yf_ticker.info['longName']

    last_fcf = yf_ticker.get_cash_flow().iloc[-1][0]
    
    url = "https://finance.yahoo.com/quote/{}/analysis?p={}".format(ticker, ticker)
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'})
    parser = html.fromstring(response.content)
    ge = parser.xpath('//table//tbody//tr')

    for row in ge:
        label = row.xpath("td/span/text()")[0]
        if 'Next 5 Years' in label:
            try:
                ge = float(row.xpath("td/text()")[0].replace('%', ''))
            except:
                ge = []
            break
    print(yf_ticker.shares.iloc[-1])
    shares = yf_ticker.shares.iloc[-1][0]
    
    eps = yf_ticker.get_financials().loc['DilutedEPS'].iloc[0]
    # in case current yearly eps cell isn't populated yet
    if math.isnan(eps):
        quarterly_earnings = yf_ticker.get_financials(freq='quarterly').loc['DilutedEPS']
        eps = 0
        for i in range(quarterly_earnings.size):
            eps += quarterly_earnings.iloc[i]
        eps = round(eps, 2)
        print(quarterly_earnings)

    market_price = yf_ticker.basic_info['last_price']
    return {'company_name' : company_name, 'fcf': last_fcf, 'ge': ge, 'shares': shares, 'eps': eps, 'mp': market_price}

def dcf(data: dict) -> dict:
    forecast = [data['fcf']]

    if data['ge'] == []:
        raise ValueError("No growth rate available from Yahoo Finance")

    for i in range(1, data['yr']):
        forecast.append(round(forecast[-1] + (data['ge'] / 100) * forecast[-1], 2))

    forecast.append(round(forecast[-1] * (1 + (data['pr'] / 100)) / (data['dr'] / 100 - data['pr'] / 100), 2)) #terminal value
    discount_factors = [1 / (1 + (data['dr'] / 100))**(i + 1) for i in range(len(forecast) - 1)]

    pvs = [round(f * d, 2) for f, d in zip(forecast[:-1], discount_factors)]
    pvs.append(round(discount_factors[-1] * forecast[-1], 2)) # discounted terminal value
    
    result = {}

    print("Forecasted cash flows: {}".format(", ".join(map(str, forecast))))

    result['forecasted_cash_flows'] = forecast

    print("PV of cash flows: {}".format(", ".join(map(str, pvs))))

    result['cashflow_present_values'] = pvs

    dcf = sum(pvs)

    print("Fair value: {}\n".format(dcf / data['shares']))

    result['fair_value'] = dcf / data['shares']

    return result

def reverse_dcf(data):
    pass

def graham(data: dict) -> dict:

    result = {}

    if data['eps'] > 0:
        expected_value = data['eps'] * (8.5 + 2 * (data['ge']))
        ge_priced_in = (data['mp'] / data['eps'] - 8.5) / 2

        print("Expected value based on growth rate: {}".format(expected_value))

        result['graham_expected_value'] = expected_value

        print("Growth rate priced in for next 7-10 years: {}\n".format(ge_priced_in))

        result['graham_growth_estimate'] = ge_priced_in

    else:
        print("Not applicable since EPS is negative.")
    return result


def get_fairval(ticker: str, discount_rate: float, perpetual_rate: float, ge: float = None, term: int = 5, eps: float = None) -> dict:

    print("Fetching data for %s...\n" % (ticker))

    data = parse(ticker)
    result = data.copy()

    if ge is not None:
        data['ge'] = ge
    if eps is not None:
        data['eps'] = eps

    data['dr'] = discount_rate
    data['pr'] = perpetual_rate
    data['yr'] = term

    print("=" * 80)
    print("DCF model (basic)")
    print("=" * 80 + "\n")


    print("Market price: {}".format(data['mp']))
    print("EPS: {}".format(data['eps']))
    print("Growth estimate: {}".format(data['ge']))
    print("Term: {} years".format(data['yr']))
    print("Discount Rate: {}%".format(data['dr']))
    print("Perpetual Rate: {}%\n".format(data['pr']))

    result.update(dcf(data))

    print("=" * 80)
    print("Graham style valuation basic (Page 295, The Intelligent Investor)")
    print("=" * 80 + "\n")

    result.update(graham(data))
    return result
    