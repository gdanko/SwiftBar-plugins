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

        plugin_output = []

        company_info = ['--Company Info']
        if 'longName' in symbol_info:
            company_info.append(f'----{symbol_info["longName"]}')
        if 'website' in symbol_info:
            company_info.append('----{symbol_info["website"]} | href={symbol_info["website"]} | color=blue')
        if 'address1' in symbol_info and 'city' in symbol_info and 'state' in symbol_info and 'zip' in symbol_info:
            company_info.append(f'----Location: {symbol_info["address1"]}, {symbol_info["city"]}, {symbol_info["state"]}, {symbol_info["zip"]}')
        if 'phone' in symbol_info:
            company_info.append(f'----Phone: {symbol_info["phone"]}')
        if 'fullTimeEmployees' in symbol_info:
            company_info.append(f'----FT Employees: {add_commas(symbol_info["fullTimeEmployees"])}')
        if 'currency' in symbol_info:
            company_info.append(f'----Currency: {symbol_info["currency"]}')

        key_stats = ['--Key Stats']
        if 'open' in symbol_info:
            key_stats.append(f'----Open: {to_dollar(symbol_info["open"])}')
        if 'dayHigh' in symbol_info:
            key_stats.append(f'----Daily High: {to_dollar(symbol_info["dayHigh"])}')
        if 'dayLow' in symbol_info:
            key_stats.append(f'----Daily Low: {to_dollar(symbol_info["dayLow"])}')
        if 'previousClose' in symbol_info:
            key_stats.append(f'----Previous Close: {to_dollar(symbol_info["previousClose"])}')
        if 'averageVolume10days' in symbol_info:
            key_stats.append(f'----10 Day Average Volume: {numerize.numerize(symbol_info["averageVolume10days"], 3)}')
        if 'fiftyTwoWeekHigh' in symbol_info:
            key_stats.append(f'----52 Week High: {to_dollar(symbol_metadata["fiftyTwoWeekHigh"])}')
        if 'fiftyTwoWeekLow' in symbol_info:
            key_stats.append(f'----52 Week Low: {to_dollar(symbol_metadata["fiftyTwoWeekLow"])}')
        if 'beta' in symbol_info:
            key_stats.append(f'----Beta: {numerize.numerize(symbol_info["beta"])}')
        if 'marketCap' in symbol_info:
            key_stats.append(f'----Market Cap: ${numerize.numerize(symbol_info["marketCap"], 3)}')
        if 'sharesOutstanding' in symbol_info:
            key_stats.append(f'----Shares Outstanding: {numerize.numerize(symbol_info["sharesOutstanding"], 3)}')
        if 'floatShares' in symbol_info:
            key_stats.append(f'----Public Float: {numerize.numerize(symbol_info["floatShares"], 3)}')
        if 'dividendRate' in symbol_info:
            key_stats.append(f'----Dividend Rate: {add_commas(symbol_info["dividendRate"])}')
        if 'dividendYield' in symbol_info:
            key_stats.append(f'----Dividend Yield: {float_to_pct(symbol_info["dividendYield"])}')
        if 'lastDividendValue' in symbol_info:
            key_stats.append(f'----Dividend: ${to_dollar(symbol_info["lastDividendValue"])}')
        if 'totalRevenue' in symbol_info:
            key_stats.append(f'----Revenue: {numerize.numerize(symbol_info["totalRevenue"])}')
        if 'totalRevenue' in symbol_info and 'fullTimeEmployees' in symbol_info:
            key_stats.append(f'----Revenue Per Employee: ${numerize.numerize((symbol_info["totalRevenue"] / symbol_info["fullTimeEmployees"]), 3)}')

        ratios_and_protiability = ['--Ratios/Profitability']
        if 'trailingEps' in symbol_info:
            ratios_and_protiability.append(f'----EPS (TTM): {to_dollar(symbol_info["trailingEps"])}')
        if 'trailingPE' in symbol_info:
            ratios_and_protiability.append(f'----P/E (TTM): {pad_float(symbol_info["trailingPE"])}')
        if 'forwardPE' in symbol_info:
            ratios_and_protiability.append(f'----Fwd P/E (NTM): {pad_float(symbol_info["forwardPE"])}')
        if 'totalRevenue' in symbol_info:
            ratios_and_protiability.append(f'----Revenue: {numerize.numerize(symbol_info["totalRevenue"], 3)}')
        if 'revenuePerShare' in symbol_info:
            ratios_and_protiability.append(f'----Revenue Per Share: {to_dollar(symbol_info["revenuePerShare"])}')
        if 'returnOnEquity' in symbol_info:
            ratios_and_protiability.append(f'----ROE (TTM): {float_to_pct(symbol_info["returnOnEquity"])}')
        if 'ebitda' in symbol_info:
            ratios_and_protiability.append(f'----EBITDA (TTM): {numerize.numerize(symbol_info["ebitda"], 3)}')
        if 'grossMargins' in symbol_info:
            ratios_and_protiability.append(f'----Gross Margin (TTM): {float_to_pct(symbol_info["grossMargins"])}')
        if 'profitMargins' in symbol_info:
            ratios_and_protiability.append(f'----Net Margin (TTM): {float_to_pct(symbol_info["profitMargins"])}')
        if 'debtToEquity' in symbol_info:
            ratios_and_protiability.append(f'----Debt To Equity (TTM): {pad_float(symbol_info["debtToEquity"])}%')

        events = ['--Events']
        if 'lastFiscalYearEnd' in symbol_info:
            events.append(f'----Last Fiscal Year End: {unix_to_human(symbol_info["lastFiscalYearEnd"])}')
        if 'nextFiscalYearEnd' in symbol_info:
            events.append(f'----Next Fiscal Year End: {unix_to_human(symbol_info["nextFiscalYearEnd"])}')
        if 'mostRecentQuarter' in symbol_info:
            events.append(f'----Most Recent Quarter: {unix_to_human(symbol_info["mostRecentQuarter"])}')
        if 'lastDividendDate' in symbol_info:
            events.append(f'----Last Dividend Date: {unix_to_human(symbol_info["lastDividendDate"])}')
        if 'firstTradeDateEpochUtc' in symbol_info:
            events.append(f'----First Trade Date: {unix_to_human(symbol_info["firstTradeDateEpochUtc"])}')
        if 'lastSplitFactor' in symbol_info and 'lastSplitDate' in symbol_info:
            events.append(f'----Last Split: {symbol_info["lastSplitFactor"]} on {unix_to_human(symbol_info["lastSplitDate"])}')

        for item in [company_info, key_stats, ratios_and_protiability, events]:
            if len(item) > 1:
                plugin_output.append('\n'.join(item))

        if len(plugin_output) > 0:
            print(symbol)
            for item in plugin_output:
                print(item)

    print('Refresh market data | refresh=true')

if __name__ == '__main__':
    main()
