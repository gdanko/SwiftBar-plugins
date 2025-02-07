#!/usr/bin/env python3

# <xbar.title>Stock Quotes</xbar.title>
# <xbar.version>v0.6.2</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show info about the specified stock symbols</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-finance-StockQuotes.15m.py</xbar.abouturl>
# <xbar.var>string(VAR_STOCK_QUOTES_DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_STOCK_SYMBOLS="AAPL"): A comma-delimited list of stock symbols</xbar.var>
# <xbar.var>string(VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED=false): Show Company Info menu</xbar.var>
# <xbar.var>string(VAR_STOCK_QUOTES_KEY_STATS_ENABLED=false): Show Key Stats menu</xbar.var>
# <xbar.var>string(VAR_STOCK_QUOTES_R_AND_P_ENABLED=false): Ratios and Profitability debugging menu</xbar.var>
# <xbar.var>string(VAR_STOCK_QUOTES_EVENTS_ENABLED=false): Show Events menu</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[VAR_STOCK_QUOTES_DEBUG_ENABLED=false, VAR_STOCK_SYMBOLS=AAPL, VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED=true, VAR_STOCK_QUOTES_KEY_STATS_ENABLED=true, VAR_STOCK_QUOTES_R_AND_P_ENABLED=true, VAR_STOCK_QUOTES_EVENTS_ENABLED=true]</swiftbar.environment>

from collections import OrderedDict
from swiftbar import images, util, yfinance
from swiftbar.plugin import Plugin
import re

def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict = OrderedDict()
    plugin.defaults_dict['VAR_STOCK_QUOTES_DEBUG_ENABLED'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--debug',
            'title': 'the "Debugging" menu',
        },
    }
    plugin.defaults_dict['VAR_STOCK_QUOTES_SYMBOLS'] = {
        'default_value': 'AAPL',
    }
    plugin.defaults_dict['VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--company-info',
            'title': 'the "Company Info" menu',
        },
    }
    plugin.defaults_dict['VAR_STOCK_QUOTES_COMPANY_OFFICERS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--company-officers',
            'title': 'the "Company Officers" menu',
        },
    }
    plugin.defaults_dict['VAR_STOCK_QUOTES_KEY_STATS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--key-stats',
            'title': 'the "Key Stats" menu',
        },
    }
    plugin.defaults_dict['VAR_STOCK_QUOTES_R_AND_P_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--r-and-p',
            'title': 'the "Ratios and Profitability" menu',
        },
    }
    plugin.defaults_dict['VAR_STOCK_QUOTES_EVENTS_ENABLED'] = {
        'default_value': True,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--events',
            'title': 'the "Events" menu',
        },
    }

    plugin.read_config()
    plugin.generate_args()
    plugin.update_json_from_args()

    plugin_output = []
    info_dict = {}

    cookie, crumb = yfinance.get_cookie_and_crumb()
    if cookie and crumb:
        for symbol in re.split(r'\s*,\s*', plugin.configuration['VAR_STOCK_QUOTES_SYMBOLS']):
            company_data = yfinance.get_quote_summary(
                cookie=cookie,
                crumb=crumb,
                modules=['financialData', 'quoteType', 'defaultKeyStatistics', 'assetProfile', 'summaryDetail'],
                symbol=symbol,
            )
            if company_data:
                info_dict[symbol] = company_data
    
        if len(info_dict) > 0:
            for symbol, info in info_dict.items():
                price = info['currentPrice']
                last = info['previousClose']
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
            for i in range (len(re.split(r'\s*,\s*', plugin.configuration['VAR_STOCK_QUOTES_SYMBOLS']))):
                symbol = re.split(r'\s*,\s*', plugin.configuration['VAR_STOCK_QUOTES_SYMBOLS'])[i]
                symbol_info = info_dict[symbol]

                company_info = OrderedDict()
                if 'longName' in symbol_info:
                    company_info['Company'] = symbol_info['longName']
                if 'website' in symbol_info:
                    company_info['Web Site'] = symbol_info['website']
                if 'irWebsite' in symbol_info:
                    company_info['Investor Relations Web Site'] = symbol_info['irWebsite']
                if 'address1' in symbol_info and 'city' in symbol_info and 'state' in symbol_info and 'zip' in symbol_info:
                    company_info['Location'] = f'{symbol_info["address1"]}, {symbol_info["city"]}, {symbol_info["state"]}, {symbol_info["zip"]}'
                if 'phone' in symbol_info:
                    company_info['Phone'] = symbol_info['phone']
                if 'fullTimeEmployees' in symbol_info:
                    company_info['FT Employees'] = util.add_commas(symbol_info['fullTimeEmployees'])
                if 'phone' in symbol_info:
                    company_info['Phone'] = symbol_info['phone']
                
                if 'companyOfficers' in symbol_info and len(symbol_info['companyOfficers']) > 0:
                    people = {}
                    for entry in symbol_info['companyOfficers']:
                        people[entry['name']] = OrderedDict()
                        if 'title' in entry:
                            people[entry['name']]['Title'] = entry['title']
                        if 'totalPay' in entry:
                            people[entry['name']]['Total Pay'] = util.numerize(entry['totalPay']['raw'])
                        if 'yearBorn' in entry:
                            people[entry['name']]['Year Born'] = entry['yearBorn']
                        if 'age' in entry:
                            people[entry['name']]['Age'] = entry['age']
                
                key_stats  = OrderedDict()
                if 'open' in symbol_info:
                    key_stats['Open'] = util.to_dollar(symbol_info['open'])
                if 'dayHigh' in symbol_info:
                    key_stats['Daily High'] = util.to_dollar(symbol_info['dayHigh'])
                if 'dayLow' in symbol_info:
                    key_stats['Daily Low'] = util.to_dollar(symbol_info['dayLow'])
                if 'previousClose' in symbol_info:
                    key_stats['Previous Close'] = util.to_dollar(symbol_info['previousClose'])
                if 'averageVolume10days' in symbol_info:
                    key_stats['10 Day Average Volume'] = util.numerize(symbol_info['averageVolume10days'])
                if 'fiftyTwoWeekHigh' in symbol_info:
                    key_stats['52 Week High'] = util.to_dollar(symbol_info['fiftyTwoWeekHigh'])
                if 'fiftyTwoWeekLow' in symbol_info:
                    key_stats['52 Week Low'] = util.to_dollar(symbol_info['fiftyTwoWeekLow'])
                if '52WeekChange' in symbol_info:
                    key_stats['52 Week Change'] = util.pad_float(symbol_info['52WeekChange']) + '%'
                if 'targetHighPrice' in symbol_info:
                    key_stats['Target High Price'] = util.to_dollar(symbol_info['targetHighPrice'])
                if 'targetLowPrice' in symbol_info:
                    key_stats['Target Low Price'] = util.to_dollar(symbol_info['targetLowPrice'])
                if 'targetMeanPrice' in symbol_info:
                    key_stats['Target Mean Price'] = util.to_dollar(symbol_info['targetMeanPrice'])
                if 'targetMedianPrice' in symbol_info:
                    key_stats['Target Median Price'] = util.to_dollar(symbol_info['targetMedianPrice'])
                if 'beta' in symbol_info:
                    key_stats['Beta'] = util.numerize(symbol_info['beta'])
                if 'marketCap' in symbol_info:
                    key_stats['Market Cap'] = '$' + util.numerize(symbol_info["marketCap"])
                if 'sharesOutstanding' in symbol_info:
                    key_stats['Shares Outstanding'] = util.numerize(symbol_info['sharesOutstanding'])
                if 'sharesShort' in symbol_info:
                    key_stats['Shares Short'] = util.numerize(symbol_info['sharesShort'])
                if 'sharesShortPriorMonth' in symbol_info:
                    key_stats['Shares Short Prior Month'] = util.numerize(symbol_info['sharesShort'])
                if 'sharesShortPreviousMonthDate' in symbol_info:
                    key_stats['Shares Short Prior Month Date'] = util.get_timestamp(symbol_info['sharesShortPreviousMonthDate'], '%Y-%m-%d')
                if 'floatShares' in symbol_info:
                    key_stats['Public Float'] = util.numerize(symbol_info['floatShares'])
                if 'dividendRate' in symbol_info:
                    key_stats['Dividend Rate'] = util.add_commas(symbol_info['dividendRate'])
                if 'dividendYield' in symbol_info:
                    key_stats['Dividend Yield'] = util.float_to_pct(symbol_info['dividendYield'])
                if 'lastDividendValue' in symbol_info:
                    key_stats['Dividend'] = util.to_dollar(symbol_info['lastDividendValue'])
                if 'totalCash' in symbol_info:
                    key_stats['Total Cash'] = '$' + util.numerize(symbol_info['totalCash'])
                if 'totalCashPerShare' in symbol_info:
                    key_stats['Total Cash/Share'] = util.to_dollar(symbol_info['totalCashPerShare'])
                if 'totalDebt' in symbol_info:
                    key_stats['Total Debt'] = '$' + util.numerize(symbol_info['totalDebt'])
                if 'recommendationKey' in symbol_info:
                    key_stats['Recommendation'] = symbol_info['recommendationKey'].title()
                if 'numberOfAnalystOpinions' in symbol_info:
                    key_stats['Recommendation'] += f' - based on {symbol_info["numberOfAnalystOpinions"]} analyists\' opinions'

                ratios_and_profitability = OrderedDict()
                if 'trailingEps' in symbol_info:
                    ratios_and_profitability['EPS (TTM)'] = util.to_dollar(symbol_info['trailingEps'])
                if 'trailingPE' in symbol_info:
                    ratios_and_profitability['P/E (TTM)'] = util.pad_float(symbol_info['trailingPE'])
                if 'forwardPE' in symbol_info:
                    ratios_and_profitability['Fwd P/E (NTM)'] = util.pad_float(symbol_info['forwardPE'])
                if 'totalRevenue' in symbol_info:
                    ratios_and_profitability['Revenue'] = '$' + util.numerize(symbol_info['totalRevenue'])
                    ratios_and_profitability['Revenue Per Employee'] = '$' + util.numerize((symbol_info["totalRevenue"] / symbol_info["fullTimeEmployees"]))
                if 'revenuePerShare' in symbol_info:
                    ratios_and_profitability['Revenue Per Share'] = util.to_dollar(symbol_info['revenuePerShare'])
                if 'returnOnEquity' in symbol_info:
                    ratios_and_profitability['ROE (TTM)'] = util.float_to_pct(symbol_info['returnOnEquity'])
                if 'ebitda' in symbol_info:
                    ratios_and_profitability['EBITDA (TTM)'] = util.numerize(symbol_info['ebitda'])
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
                
                if (plugin.configuration['VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED'] and len(company_info) > 0) or (plugin.configuration['VAR_STOCK_QUOTES_KEY_STATS_ENABLED'] and len(key_stats) > 0) or (plugin.configuration['VAR_STOCK_QUOTES_R_AND_P_ENABLED'] and len(ratios_and_profitability) > 0) or (plugin.configuration['VAR_STOCK_QUOTES_EVENTS_ENABLED'] and len(events) > 0):
                    plugin.print_menu_item(symbol)

                if plugin.configuration['VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED']:
                    if len(company_info) > 0:
                        plugin.print_menu_item('--Company Info')
                        plugin.print_ordered_dict(company_info, justify='left', indent=4)
                
                if plugin.configuration['VAR_STOCK_QUOTES_COMPANY_OFFICERS_ENABLED']:
                    if len(people) > 0:
                        plugin.print_menu_item('--Company Officers')
                        for person, data in people.items():
                            plugin.print_menu_item(f'----{person}')
                            plugin.print_ordered_dict(data, justify='left', indent=6)

                if plugin.configuration['VAR_STOCK_QUOTES_KEY_STATS_ENABLED']:
                    if len(key_stats) > 0:
                        plugin.print_menu_item('--Key Stats')
                        plugin.print_ordered_dict(key_stats, justify='left', indent=4)

                if plugin.configuration['VAR_STOCK_QUOTES_R_AND_P_ENABLED']:
                    if len(ratios_and_profitability) > 0:
                        plugin.print_menu_item('--Ratios and Profitability')
                        plugin.print_ordered_dict(ratios_and_profitability, justify='left', indent=4)

                if plugin.configuration['VAR_STOCK_QUOTES_EVENTS_ENABLED']:
                    if len(events) > 0:
                        plugin.print_menu_item('--Events')
                        plugin.print_ordered_dict(events, justify='left', indent=4)
        else:
            plugin.print_menu_title('Stock Quotes: N/A')
            plugin.print_menu_item('No data found')
    else:
        plugin.print_menu_title('Stock Quotes: Error')
        plugin.print_menu_item('Failed to get a Yahoo! Finance crumb')

    plugin.print_menu_separator()
    if plugin.defaults_dict:
        plugin.display_settings_menu()
    if plugin.configuration['VAR_STOCK_QUOTES_DEBUG_ENABLED']:
        plugin.display_debugging_menu()
    plugin.print_menu_item('Refresh market data', refresh=True)
if __name__ == '__main__':
    main()
