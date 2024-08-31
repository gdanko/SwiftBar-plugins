#!/usr/bin/env python3

# <xbar.title>Stock Indexes</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>This plugin shows info about the specified stock symbols</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Finance/gdanko-finance-StockIndexes.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_STOCK_SYMBOLS="AAPL"): A comma-delimited list of stock symbols</xbar.var>

import os
import re
from pprint import pprint

def pad_float(number):
    return '{:.2f}'.format(float(number))

def main():
    try:
        import yfinance

        output = []
        default_symbols = 'AAPL'
        symbols = os.getenv('VAR_STOCK_SYMBOLS', default_symbols)

        if symbols != '':
            symbols = default_symbols
        symbols_list = re.split(r'\s*,\s*', symbols)

        tickers = yfinance.Tickers(' '.join(symbols_list))

        for symbol in symbols_list:
            info = tickers.tickers[symbol].info
            tickers.tickers[symbol].history(period="1d")
            metadata= tickers.tickers[symbol].history_metadata

            price = metadata['regularMarketPrice']
            last = info['previousClose']

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
