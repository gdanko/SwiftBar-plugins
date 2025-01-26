#!/usr/bin/env python3

# <xbar.title>Stock Quotes</xbar.title>
# <xbar.version>v0.3.0</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show info about the specified stock symbols</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-finance-StockQuotes.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_STOCK_SYMBOLS="AAPL"): A comma-delimited list of stock symbols</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>

from collections import OrderedDict
from swiftbar import util
from swiftbar.plugin import Plugin
import argparse
import re
import subprocess
import sys

try:
    from numerize import numerize
    import yfinance
except ModuleNotFoundError:
    print('Error: missing "numerize" and "yfinance" libraries.')
    print('---')

    subprocess.run('pbcopy', universal_newlines=True, nput=f'{sys.executable} -m pip install numerize yfinance')
    print('Fix copied to clipboard. Paste on terminal and run.')
    exit(1)

def configure():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='Toggle viewing the debug section', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args

def main():
    plugin = Plugin()
    defaults_dict = {
        'VAR_STOCK_QUOTES_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_STOCK_QUOTES_SYMBOLS': {
            'default_value': 'AAPL',
            'split_value': True,
        },
    }
    plugin.read_config(defaults_dict)
    args = configure()

    if args.debug:
        plugin.update_setting('VAR_STOCK_QUOTES_DEBUG_ENABLED', True if plugin.configuration['VAR_STOCK_QUOTES_DEBUG_ENABLED'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_STOCK_QUOTES_DEBUG_ENABLED']
    symbols = re.split(r'\s*,\s*', plugin.configuration['VAR_STOCK_QUOTES_SYMBOLS'])
    plugin_output = []
    info_dict = {}
    metadata_dict = {}

    tickers = yfinance.Tickers(' '.join(symbols))

    for symbol in symbols:
        info = tickers.tickers[symbol].info
        tickers.tickers[symbol].history(period="1d")
        metadata = tickers.tickers[symbol].history_metadata
        price = info['currentPrice']
        last = info['previousClose']

        info_dict[symbol] = info
        metadata_dict[symbol] = metadata

        if price > last:
            updown = u'\u2191'
            updown_amount = f'+{util.pad_float((price - last))}'
            pct_change = f'+{util.pad_float((price - last) / last * 100)}'
        else:
            updown = u'\u2193'
            updown_amount = f'-{util.pad_float((float(last - price)))}'
            pct_change = f'-{util.pad_float((last - price) / last * 100)}'

        plugin_output.append(f'{symbol} {util.pad_float(price)} {updown} {updown_amount} ({pct_change}%)')
    plugin.print_menu_title('; '.join(plugin_output))
    plugin.print_menu_separator()
    plugin.print_update_time()
    plugin.print_menu_separator()
    for i in range (len(symbols)):
        symbol = symbols[i]
        symbol_info = info_dict[symbol]
        symbol_metadata = metadata_dict[symbol]

        plugin.print_menu_item(symbol)
        company_info = OrderedDict()
        if 'longName' in symbol_info:
            company_info['Company'] = symbol_info['longName']
        if 'website' in symbol_info:
            company_info['Web Site'] = symbol_info['website']
        if 'address1' in symbol_info and 'city' in symbol_info and 'state' in symbol_info and 'zip' in symbol_info:
            company_info['Location'] = f'{symbol_info["address1"]}, {symbol_info["city"]}, {symbol_info["state"]}, {symbol_info["zip"]}'
        if 'phone' in symbol_info:
            company_info['Phone'] = symbol_info['phone']
        if 'fullTimeEmployees' in symbol_info:
            company_info['FT Employees'] = util.add_commas(symbol_info['fullTimeEmployees'])
        if 'currency' in symbol_info:
            company_info['Phone'] = symbol_info['phone']

        key_stats = OrderedDict()
        if 'open' in symbol_info:
            key_stats['Open'] = util.to_dollar(symbol_info['open'])
        if 'dayHigh' in symbol_info:
            key_stats['Daily High'] = util.to_dollar(symbol_info['dayHigh'])
        if 'dayLow' in symbol_info:
            key_stats['Daily Low'] = util.to_dollar(symbol_info['dayLow'])
        if 'previousClose' in symbol_info:
            key_stats['Previous Close'] = util.to_dollar(symbol_info['previousClose'])
        if 'averageVolume10days' in symbol_info:
            key_stats['10 Day Average Volume'] = numerize.numerize(symbol_info['averageVolume10days'], 3)
        if 'fiftyTwoWeekHigh' in symbol_info:
            key_stats['52 Week High'] = util.to_dollar(symbol_metadata['fiftyTwoWeekHigh'])
        if 'fiftyTwoWeekLow' in symbol_info:
            key_stats['52 Week Low'] = util.to_dollar(symbol_metadata['fiftyTwoWeekLow'])
        if 'beta' in symbol_info:
            key_stats['Beta'] = numerize.numerize(symbol_info['beta'])
        if 'marketCap' in symbol_info:
            key_stats['Market Cap'] = '$' + numerize.numerize(symbol_info["marketCap"], 3)
        if 'sharesOutstanding' in symbol_info:
            key_stats['Shares Outstanding'] = numerize.numerize(symbol_info['sharesOutstanding'], 3)
        if 'floatShares' in symbol_info:
            key_stats['Public Float'] = numerize.numerize(symbol_info['floatShares'], 3)
        if 'dividendRate' in symbol_info:
            key_stats['Dividend Rate'] = util.add_commas(symbol_info['dividendRate'])
        if 'dividendYield' in symbol_info:
            key_stats['Dividend Yield'] = util.float_to_pct(symbol_info['dividendYield'])
        if 'lastDividendValue' in symbol_info:
            key_stats['Dividend'] = util.to_dollar(symbol_info['lastDividendValue'])
        if 'totalRevenue' in symbol_info:
            key_stats['Revenue'] = numerize.numerize(symbol_info['totalRevenue'])
        if 'totalRevenue' in symbol_info and 'fullTimeEmployees' in symbol_info:
            key_stats['Revenue Per Employee'] = '$' + numerize.numerize((symbol_info["totalRevenue"] / symbol_info["fullTimeEmployees"]), 3)

        ratios_and_profitability = OrderedDict()
        if 'trailingEps' in symbol_info:
            ratios_and_profitability['EPS (TTM)'] = util.to_dollar(symbol_info['trailingEps'])
        if 'trailingPE' in symbol_info:
            ratios_and_profitability['P/E (TTM)'] = util.pad_float(symbol_info['trailingPE'])
        if 'forwardPE' in symbol_info:
            ratios_and_profitability['Fwd P/E (NTM)'] = util.pad_float(symbol_info['forwardPE'])
        if 'totalRevenue' in symbol_info:
            ratios_and_profitability['Revenue'] = '$' + numerize.numerize(symbol_info['totalRevenue'], 3)
        if 'revenuePerShare' in symbol_info:
            ratios_and_profitability['Revenue Per Share'] = util.to_dollar(symbol_info['revenuePerShare'])
        if 'returnOnEquity' in symbol_info:
            ratios_and_profitability['ROE (TTM)'] = util.float_to_pct(symbol_info['returnOnEquity'])
        if 'ebitda' in symbol_info:
            ratios_and_profitability['EBITDA (TTM)'] = numerize.numerize(symbol_info['ebitda'], 3)
        if 'grossMargins' in symbol_info:
            ratios_and_profitability['Gross Margin (TTM)'] = util.float_to_pct(symbol_info['grossMargins'])
        if 'profitMargins' in symbol_info:
            ratios_and_profitability['Net Margin (TTM)'] = util.float_to_pct(symbol_info['profitMargins'])
        if 'debtToEquity' in symbol_info:
            ratios_and_profitability['Debt To Equity (TTM)'] = util.pad_float(symbol_info['debtToEquity']) + '%'

        events = OrderedDict()
        if 'lastFiscalYearEnd' in symbol_info:
            events['Last Fiscal Year End'] = util.unix_to_human(symbol_info['lastFiscalYearEnd'])
        if 'nextFiscalYearEnd' in symbol_info:
            events['Next Fiscal Year End'] = util.unix_to_human(symbol_info['nextFiscalYearEnd'])
        if 'mostRecentQuarter' in symbol_info:
            events['Most Recent Quarter'] = util.unix_to_human(symbol_info['mostRecentQuarter'])
        if 'lastDividendDate' in symbol_info:
            events['Last Dividend Date'] = util.unix_to_human(symbol_info['lastDividendDate'])
        if 'firstTradeDateEpochUtc' in symbol_info:
            events['First Trade Date'] = util.unix_to_human(symbol_info['firstTradeDateEpochUtc'])
        if 'lastSplitFactor' in symbol_info and 'lastSplitDate' in symbol_info:
            events['Last Split'] = f'{symbol_info["lastSplitFactor"]} on {util.unix_to_human(symbol_info["lastSplitDate"])}'

        if len(company_info) > 0:
            plugin.print_menu_item('--Company Info')
            plugin.print_ordered_dict(company_info, justify='left', indent=4)

        if len(key_stats) > 0:
            plugin.print_menu_item('--Key Stats')
            plugin.print_ordered_dict(key_stats, justify='left', indent=4)

        if len(ratios_and_profitability) > 0:
            plugin.print_menu_item('--Ratios and Profitability')
            plugin.print_ordered_dict(ratios_and_profitability, justify='left', indent=4)

        if len(events) > 0:
            plugin.print_menu_item('--Events')
            plugin.print_ordered_dict(events, justify='left', indent=4)

    plugin.print_menu_separator()
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} debug data',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
    )
    if debug_enabled:
        plugin.display_debug_data()
    plugin.print_menu_item('Refresh market data', refresh=True)

if __name__ == '__main__':
    main()
