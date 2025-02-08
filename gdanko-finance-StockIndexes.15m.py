#!/usr/bin/env python3

# <xbar.title>Stock Indexes</xbar.title>
# <xbar.version>v0.3.1</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show info about the DOW, NASDAQ, S&P indexes</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-finance-StockIndexes.15m.py</xbar.abouturl>
# <xbar.var>string(DEBUG_ENABLED=false): Show debugging menu</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[DEBUG_ENABLED=false]</swiftbar.environment>

from collections import OrderedDict
from swiftbar import images, util, yfinance
from swiftbar.plugin import Plugin

def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict = OrderedDict()
    plugin.defaults_dict['DEBUG_ENABLED'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': None,
            'flag': '--debug',
            'title': 'the "Debugging" menu',
        },
    }

    plugin.read_config()
    plugin.generate_args()
    plugin.update_json_from_args()

    plugin_output = []
    cookie, crumb = yfinance.get_cookie_and_crumb()
    if cookie and crumb:
        symbol_map = {
            'Dow': '^DJI',
            'Nasdaq': '^IXIC',
            'S&P500': '^GSPC',
        }
        for key, value in symbol_map.items():
            index_data = yfinance.get_chart(cookie=cookie, crumb=crumb, symbol=value)
            if index_data:
                price = index_data['regularMarketPrice']
                last = index_data['previousClose']

                if price > last:
                    updown = u'\u2191'
                    pct_change = f'{util.pad_float((price - last) / last * 100)}%'
                else:
                    updown = u'\u2193'
                    pct_change = f'{util.pad_float((last - price) / last * 100)}%'

                plugin_output.append(f'{key} {updown} {pct_change}')
        plugin.print_menu_title('; '.join(plugin_output))

    else:
        plugin.print_menu_title('Stock Indexes: Error')
        plugin.print_menu_item('Failed to get a Yahoo! Finance crumb')
    plugin.render_footer()

if __name__ == '__main__':
    main()
