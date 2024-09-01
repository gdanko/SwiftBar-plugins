#!/usr/bin/env python3

# <xbar.title>Stock Indexes</xbar.title>
# <xbar.version>v0.1.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show info about the DOW, NASDAQ, S&P indexes</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/Finance/gdanko-finance-StockIndexes.15m.py</xbar.abouturl>

def pad_float(number):
    return '{:.2f}'.format(float(number))

def main():
    try:
        import yfinance

        output = []
        symbol_map = {
            'Dow': '^DJI',
            'Nasdaq': '^IXIC',
            'S&P500': '^GSPC',
        }

        tickers = yfinance.Tickers('^DJI ^IXIC ^GSPC')

        for key, value in symbol_map.items():
            info = tickers.tickers[value].info
            tickers.tickers[value].history(period="1d")
            metadata= tickers.tickers[value].history_metadata

            price = metadata['regularMarketPrice']
            last = info['previousClose']

            if price > last:
                updown = u'\u2191'
                pct_change = f'{pad_float((price - last) / last * 100)}%'
            else:
                updown = u'\u2193'
                pct_change = f'{pad_float((last - price) / last * 100)}%'
            
            output.append(f'{key} {updown} {pct_change}')
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
