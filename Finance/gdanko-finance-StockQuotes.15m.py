#!/usr/bin/env python3

# <xbar.title>Stock Indexes</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show info about the specified stock symbols</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Finance/gdanko-finance-StockIndexes.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_STOCK_SYMBOLS="AAPL"): A comma-delimited list of stock symbols</xbar.var>

import datetime
import os
import re
import subprocess
import sys
import time

try:
    from numerize import numerize
    import yfinance
except ModuleNotFoundError:
    print('Error: missing "numerize" and "yfinance" libraries.')
    print('---')

    subprocess.run('pbcopy', universal_newlines=True, nput=f'{sys.executable} -m pip install numerize yfinance')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def pad_float(number):
    return '{:.2f}'.format(float(number))

def get_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %k:%M:%S')

def to_dollar(number):
    return '${:,.2f}'.format(number)

def add_commas(number):
    return '{:,.0f}'.format(number)

def unix_to_human(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def float_to_pct(number):
    return f'{number:.2%}'

def main():
    output = []
    info_dict = {}
    metadata_dict = {}
    default_symbols = 'AAPL'
    symbols = os.getenv('VAR_STOCK_SYMBOLS', default_symbols)

    if symbols == '':
        symbols = default_symbols
    symbols_list = re.split(r'\s*,\s*', symbols)

    tickers = yfinance.Tickers(' '.join(symbols_list))

    for symbol in symbols_list:
        info = tickers.tickers[symbol].info
        tickers.tickers[symbol].history(period="1d")
        metadata = tickers.tickers[symbol].history_metadata
        price = info['currentPrice']
        last = info['previousClose']

        info_dict[symbol] = info
        metadata_dict[symbol] = metadata

        if price > last:
            updown = u'\u2191'
            updown_amount = f'+{pad_float((price - last))}'
            pct_change = f'+{pad_float((price - last) / last * 100)}'
        else:
            updown = u'\u2193'
            updown_amount = f'-{pad_float((float(last - price)))}'
            pct_change = f'-{pad_float((last - price) / last * 100)}'

        output.append(f'{symbol} {pad_float(price)} {updown} {updown_amount} ({pct_change}%)')
    print('; '.join(output))
    print('---')
    print(f'Updated {get_timestamp(int(time.time()))}')
    print('---')
    for i in range (len(symbols_list)):
        symbol = symbols_list[i]
        symbol_info = info_dict[symbol]
        symbol_metadata = metadata_dict[symbol]

        print(symbol)
        print('--Company Info')
        print(f'----{symbol_metadata["longName"]}')
        print(f'----{symbol_info["website"]} | href={symbol_info["website"]} | color=blue')
        print(f'----Location: {symbol_info["address1"]}, {symbol_info["city"]}, {symbol_info["state"]}, {symbol_info["zip"]}')
        print(f'----Phone: {symbol_info["phone"]}')
        print(f'----FT Employees: {add_commas(symbol_info["fullTimeEmployees"])}')
        print(f'----Currency: {symbol_info["currency"]}')
        print('--Key Stats')
        print(f'----Open: {to_dollar(symbol_info["open"])}')
        print(f'----Daily High: {to_dollar(symbol_info["dayHigh"])}')
        print(f'----Daily Low: {to_dollar(symbol_info["dayLow"])}')
        print(f'----Previous Close: {to_dollar(symbol_info["previousClose"])}')
        print(f'----10 Day Average Volume: {numerize.numerize(symbol_info["averageVolume10days"], 3)}')
        print(f'----52 Week High: {to_dollar(symbol_metadata["fiftyTwoWeekHigh"])}')
        print(f'----52 Week Low: {to_dollar(symbol_metadata["fiftyTwoWeekLow"])}')
        print(f'----Beta: {numerize.numerize(symbol_info["beta"])}')
        print(f'----Market Cap: ${numerize.numerize(symbol_info["marketCap"], 3)}')
        print(f'----Shares Outstanding: {numerize.numerize(symbol_info["sharesOutstanding"], 3)}')
        print(f'----Public Float: {numerize.numerize(symbol_info["floatShares"], 3)}')
        print(f'----Dividend Rate: {add_commas(symbol_info["dividendRate"])}')
        print(f'----Dividend Yield: {float_to_pct(symbol_info["dividendYield"])}')
        print(f'----Dividend: ${to_dollar(symbol_info["lastDividendValue"])}')
        print(f'----Revenue: {numerize.numerize(symbol_info["totalRevenue"])}')
        print(f'----Revenue Per Employee: ${numerize.numerize((symbol_info["totalRevenue"] / symbol_info["fullTimeEmployees"]), 3)}')
        print('--Ratios/Profitability')
        print(f'----EPS (TTM): {to_dollar(symbol_info["trailingEps"])}')
        print(f'----P/E (TTM): {pad_float(symbol_info["trailingPE"])}')
        print(f'----Fwd P/E (NTM): {pad_float(symbol_info["forwardPE"])}')
        print(f'----Revenue: {numerize.numerize(symbol_info["totalRevenue"], 3)}')
        print(f'----Revenue Per Share: {to_dollar(symbol_info["revenuePerShare"])}')
        print(f'----ROE (TTM): {float_to_pct(symbol_info["returnOnEquity"])}')
        print(f'----EBITDA (TTM): {numerize.numerize(symbol_info["ebitda"], 3)}')
        print(f'----Gross Margin (TTM): {float_to_pct(symbol_info["grossMargins"])}')
        print(f'----Net Margin (TTM): {float_to_pct(symbol_info["profitMargins"])}')
        print(f'----Debt To Equity (TTM): {pad_float(symbol_info["debtToEquity"])}%')
        print('--Events')
        print(f'----Last Fiscal Year End: {unix_to_human(symbol_info["lastFiscalYearEnd"])}')
        print(f'----Next Fiscal Year End: {unix_to_human(symbol_info["nextFiscalYearEnd"])}')
        print(f'----Most Recent Quarter: {unix_to_human(symbol_info["mostRecentQuarter"])}')
        print(f'----Last Dividend Date: {unix_to_human(symbol_info["lastDividendDate"])}')
        print(f'----First Trade Date: {unix_to_human(symbol_info["firstTradeDateEpochUtc"])}')
        print(f'----Last Split: {symbol_info["lastSplitFactor"]} on {unix_to_human(symbol_info["lastSplitDate"])}')

    print('Refresh market data | refresh=true')

if __name__ == '__main__':
    main()
