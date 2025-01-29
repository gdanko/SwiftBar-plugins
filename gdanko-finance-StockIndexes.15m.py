#!/usr/bin/env python3

# <xbar.title>Stock Indexes</xbar.title>
# <xbar.version>v0.2.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show info about the DOW, NASDAQ, S&P indexes</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-finance-StockIndexes.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_STOCK_INDEXES_DEBUG_ENABLED=false): Show debugging menu</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>false</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_STOCK_INDEXES_DEBUG_ENABLED=false]</swiftbar.environment>

from swiftbar import images, util
from swiftbar.plugin import Plugin
import subprocess
import sys

try:
    import yfinance
except ModuleNotFoundError:
    print('Error: missing "yfinance" library.')
    print('---')

    subprocess.run('pbcopy', universal_newlines=True, input=f'{sys.executable} -m pip install yfinance')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def main():
    plugin = Plugin()
    plugin_output = []
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
            pct_change = f'{util.pad_float((price - last) / last * 100)}%'
        else:
            updown = u'\u2193'
            pct_change = f'{util.pad_float((last - price) / last * 100)}%'

        plugin_output.append(f'{key} {updown} {pct_change}')
    plugin.print_menu_title('; '.join(plugin_output))
    plugin.print_menu_separator()
    plugin.print_update_time()

if __name__ == '__main__':
    main()
