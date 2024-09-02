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
import json
from pprint import pprint

def pad_float(number):
    return '{:.2f}'.format(float(number))

def to_dollar(number):
    return '${:,.2f}'.format(number)

def add_commas(number):
    return '{:,.0f}'.format(number)

def unix_to_human(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def main():
    try:
        import yfinance

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
            
            output.append(f'{symbol} ${pad_float(price)} {updown} {updown_amount} ({pct_change}%)')
        print('; '.join(output))
        print('---')
        for i in range (len(symbols_list)):
            symbol = symbols_list[i]
            symbol_info = info_dict[symbol]
            symbol_metadata = metadata_dict[symbol]

            print(symbol)
            print(f'--{symbol_metadata["longName"]}')
            print(f'--{symbol_info["website"]} | href={symbol_info["website"]} | color=blue')
            print(f'--Location: {symbol_info["address1"]}, {symbol_info["city"]}, {symbol_info["state"]}, {symbol_info["zip"]}')
            print(f'--Phone: {symbol_info["phone"]}')
            print(f'--FT Employees: {add_commas(symbol_info["fullTimeEmployees"])}')
            print(f'--Currency: {symbol_info["currency"]}')
            print(f'--Open: ${pad_float(symbol_info["open"])}')
            print(f'--Previous Close: ${pad_float(symbol_info["previousClose"])}')
            print(f'--Daily Low: ${pad_float(symbol_info["dayLow"])}')
            print(f'--Daily High: ${pad_float(symbol_info["dayHigh"])}')
            print(f'--52 Week Low: ${pad_float(symbol_metadata["fiftyTwoWeekLow"])}')
            print(f'--52 Week High: ${pad_float(symbol_metadata["fiftyTwoWeekHigh"])}')
            print(f'--Regular Market Volume: {add_commas(symbol_info["regularMarketVolume"])}')
            print(f'--Average Daily Volume: {add_commas(symbol_info["averageVolume"])}')
            print(f'--10 Day Average Volume: {add_commas(symbol_info["averageVolume10days"])}')
            print(f'--10 Day Average Daily Volume: {add_commas(symbol_info["averageDailyVolume10Day"])}')
            print(f'--50 Day Average: {to_dollar(symbol_info["fiftyDayAverage"])}')
            print(f'--200 Day Average: {to_dollar(symbol_info["twoHundredDayAverage"])}')
            print(f'--Market Recommendation: {symbol_info["recommendationKey"].title()}')
            print(f'--Shares Outstanding: {add_commas(symbol_info["sharesOutstanding"])}')
            print(f'--Shares Short: {add_commas(symbol_info["sharesShort"])}')
            print(f'--Shares Short Prior Month: {add_commas(symbol_info["sharesShortPriorMonth"])}')
            print(f'--Shares Short Previous Month Date: {add_commas(symbol_info["sharesShortPreviousMonthDate"])}')
            print(f'--Last Fiscal Year End: {unix_to_human(symbol_info["lastFiscalYearEnd"])}')
            print(f'--Next Fiscal Year End: {unix_to_human(symbol_info["nextFiscalYearEnd"])}')
            print(f'--Most Recent Quarter: {unix_to_human(symbol_info["mostRecentQuarter"])}')
            print(f'--Last Dividend Date: {unix_to_human(symbol_info["lastDividendDate"])}')
            print(f'--First Trade Date: {unix_to_human(symbol_info["firstTradeDateEpochUtc"])}')
            print(f'--Last Split: {symbol_info["lastSplitFactor"]} on {unix_to_human(symbol_info["lastSplitDate"])}')
            print(f'--Market Cap: {to_dollar(symbol_info["marketCap"])}')
            print('--Officers')
            for officer in symbol_info["companyOfficers"]:
                print(f'----{officer["title"]}')
                print(f'------Name: {officer["name"]}')
                if 'yearBorn' in officer:
                    print(f'------Year Born: {officer["yearBorn"]}')
                if 'age' in officer:
                    print(f'------Age: {officer["age"]}')
                if 'totalPay' in officer:
                    print(f'------Total Pay: {to_dollar(officer["totalPay"])}')
        print('Refresh market data | refresh=true')

    except ModuleNotFoundError:
        print('Error: missing "yfinance" library.')
        print('---')
        import sys
        import subprocess
        subprocess.run('pbcopy', universal_newlines=True,
                       input=f'{sys.executable} -m pip install yfinance')
        print('Fix copied to clipboard. Paste on terminal and run.')

if __name__ == '__main__':
    main()
