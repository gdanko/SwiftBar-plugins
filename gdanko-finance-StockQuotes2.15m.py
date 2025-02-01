#!/usr/bin/env python3

# <xbar.title>Stock Quotes</xbar.title>
# <xbar.version>v0.4.0</xbar.version>
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
from pprint import pprint
from swiftbar import images, request, util
from swiftbar.plugin import Plugin
import argparse
import re

def configure() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='VAR_STOCK_QUOTES_DEBUG_ENABLED', required=False, default=False, action='store_true')
    parser.add_argument('--company-info', help='VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED', required=False, default=False, action='store_true')
    parser.add_argument('--key-stats', help='VAR_STOCK_QUOTES_KEY_STATS_ENABLED', required=False, default=False, action='store_true')
    parser.add_argument('--r-and-p', help='VAR_STOCK_QUOTES_R_AND_P_ENABLED', required=False, default=False, action='store_true')
    parser.add_argument('--events', help='VAR_STOCK_QUOTES_EVENTS_ENABLED', required=False, default=False, action='store_true')
    args = parser.parse_args()
    return args

def get_yf_cookie_and_crumb(useragent: str=None):
    response, _, _ = request.swiftbar_request(
        host='fc.yahoo.com',
    )
    cookie = next((h[1] for h in response.headers.items() if h[0] == 'Set-Cookie'), None)
    if not cookie:
        return None, None

    response, crumb, err = request.swiftbar_request(
        host='query2.finance.yahoo.com',
        path='/v1/test/getcrumb',
        headers={'Cookie': cookie, 'User-Agent': useragent},
        return_type='text',
    )
    if response.status == 200 and crumb:
        return cookie, crumb
    else:
        return None, None

def get_yf_data(crumb: str=None, cookie: str=None, symbol: str=None):
    headers = {'Cookie': cookie, 'User-Agent': request.get_useragent()}
    response, output, _ = request.swiftbar_request(
        host='query2.finance.yahoo.com',
        path=f'/v10/finance/quoteSummary/{symbol}',
        query={
            'corsDomain': 'finance.yahoo.com',
            'crumb': crumb,
            'formatted': False,
            'modules': 'financialData,quoteType,defaultKeyStatistics,assetProfile,summaryDetail',
            'symbol': symbol,
        },
        headers=headers,
        return_type='json',
    )                
    if response.status == 200 and output:
        info = output['quoteSummary']['result'][0]
        company_data = {}
        for category in ['assetProfile', 'summaryDetail', 'defaultKeyStatistics', 'quoteType', 'financialData']:
            for k, v in info[category].items():
                company_data[k] = v
        return company_data
    else:
        return None

def main() -> None:
    plugin = Plugin()
    defaults_dict = {
        'VAR_STOCK_QUOTES_DEBUG_ENABLED': {
            'default_value': False,
            'valid_values': [True, False],
        },
        'VAR_STOCK_QUOTES_SYMBOLS': {
            'default_value': 'AAPL',
        },
        'VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED': {
            'default_value': True,
            'valid_values': [True, False],
        },
        'VAR_STOCK_QUOTES_KEY_STATS_ENABLED': {
            'default_value': True,
            'valid_values': [True, False],
        },
        'VAR_STOCK_QUOTES_R_AND_P_ENABLED': {
            'default_value': True,
            'valid_values': [True, False],
        },
        'VAR_STOCK_QUOTES_EVENTS_ENABLED': {
            'default_value': True,
            'valid_values': [True, False],
        },
    }
    plugin.read_config(defaults_dict)
    args = configure()

    if args.debug:
        plugin.update_setting('VAR_STOCK_QUOTES_DEBUG_ENABLED', True if plugin.configuration['VAR_STOCK_QUOTES_DEBUG_ENABLED'] == False else False)
    elif args.company_info:
        plugin.update_setting('VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED', True if plugin.configuration['VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED'] == False else False)
    elif args.key_stats:
        plugin.update_setting('VAR_STOCK_QUOTES_KEY_STATS_ENABLED', True if plugin.configuration['VAR_STOCK_QUOTES_KEY_STATS_ENABLED'] == False else False)
    elif args.r_and_p:
        plugin.update_setting('VAR_STOCK_QUOTES_R_AND_P_ENABLED', True if plugin.configuration['VAR_STOCK_QUOTES_R_AND_P_ENABLED'] == False else False)
    elif args.events:
        plugin.update_setting('VAR_STOCK_QUOTES_EVENTS_ENABLED', True if plugin.configuration['VAR_STOCK_QUOTES_EVENTS_ENABLED'] == False else False)

    plugin.read_config(defaults_dict)
    debug_enabled = plugin.configuration['VAR_STOCK_QUOTES_DEBUG_ENABLED']
    symbols = re.split(r'\s*,\s*', plugin.configuration['VAR_STOCK_QUOTES_SYMBOLS'])
    company_info_enabled = plugin.configuration['VAR_STOCK_QUOTES_COMPANY_INFO_ENABLED']
    key_stats_enabled = plugin.configuration['VAR_STOCK_QUOTES_KEY_STATS_ENABLED']
    r_and_p_enabled = plugin.configuration['VAR_STOCK_QUOTES_R_AND_P_ENABLED']
    events_enabled = plugin.configuration['VAR_STOCK_QUOTES_EVENTS_ENABLED']
    useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    plugin_output = []
    info_dict = {}

    cookie, crumb = get_yf_cookie_and_crumb(useragent)
    if cookie and crumb:
        for symbol in symbols:
            company_data = get_yf_data(cookie=cookie, crumb=crumb, symbol=symbol)
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
            for i in range (len(symbols)):
                symbol = symbols[i]
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
                
                if (company_info_enabled and len(company_info) > 0) or (key_stats_enabled and len(key_stats) > 0) or (r_and_p_enabled and len(ratios_and_profitability) > 0) or (events_enabled and len(events) > 0):
                    plugin.print_menu_item(symbol)

                if company_info_enabled:
                    if len(company_info) > 0:
                        plugin.print_menu_item('--Company Info')
                        plugin.print_ordered_dict(company_info, justify='left', indent=4)
                
                # if len(people) > 0:
                #     plugin.print_menu_item('--Company Officers')
                #     for person, data in people.items():
                #         plugin.print_menu_item(f'----{person}')
                #         plugin.print_ordered_dict(data, justify='left', indent=6)

                if key_stats_enabled:
                    if len(key_stats) > 0:
                        plugin.print_menu_item('--Key Stats')
                        plugin.print_ordered_dict(key_stats, justify='left', indent=4)

                if r_and_p_enabled:
                    if len(ratios_and_profitability) > 0:
                        plugin.print_menu_item('--Ratios and Profitability')
                        plugin.print_ordered_dict(ratios_and_profitability, justify='left', indent=4)

                if events_enabled:
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
    plugin.print_menu_item('Settings')
    plugin.print_menu_item(
        f'{"--Disable" if debug_enabled else "--Enable"} "Debugging" menu',
        cmd=[plugin.plugin_name, '--debug'],
        terminal=False,
        refresh=True,
    )
    plugin.print_menu_item(
        f'{"--Disable" if company_info_enabled else "--Enable"} "Company Info" menu',
        cmd=[plugin.plugin_name, '--company-info'],
        terminal=False,
        refresh=True,
    )
    plugin.print_menu_item(
        f'{"--Disable" if key_stats_enabled else "--Enable"} "Key Stats" menu',
        cmd=[plugin.plugin_name, '--key-stats'],
        terminal=False,
        refresh=True,
    )
    plugin.print_menu_item(
        f'{"--Disable" if r_and_p_enabled else "--Enable"} "Ratios and Profitability" menu',
        cmd=[plugin.plugin_name, '--r-and-p'],
        terminal=False,
        refresh=True,
    )
    plugin.print_menu_item(
        f'{"--Disable" if events_enabled else "--Enable"} "Events" menu',
        cmd=[plugin.plugin_name, '--events'],
        terminal=False,
        refresh=True,
    )
    if debug_enabled:
        plugin.display_debugging_menu()
    plugin.print_menu_item('Refresh market data', refresh=True)
if __name__ == '__main__':
    main()
