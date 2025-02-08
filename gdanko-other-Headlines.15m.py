#!/usr/bin/env python3

# <xbar.title>Headlines</xbar.title>
# <xbar.version>v0.1.1</xbar.version>
# <xbar.author>Gary Danko</xbar.author>
# <xbar.author.github>gdanko</xbar.author.github>
# <xbar.desc>Show headlines from the Guardian UK, requires free Guardian UK API Key</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.abouturl>https://github.com/gdanko/xbar-plugins/blob/main/gdanko-other-Headlines.15m.py</xbar.abouturl>
# <xbar.var>string(DEBUG_ENABLED=false): Show debugging menu</xbar.var>
# <xbar.var>string(VAR_HEADLINES_LIMIT=20): The maximum headlines to display</xbar.var>
# <xbar.var>string(VAR_HEADLINES_API_KEY=): The required Guardian UK API key</xbar.var>
# <xbar.var>string(VAR_HEADLINES_SECTION=world): The section to view</xbar.var>

# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
# <swiftbar.hideSwiftBar>false</swiftbar.hideSwiftBar>
# <swiftbar.environment>[DEBUG_ENABLED=false, VAR_HEADLINES_LIMIT=20, VAR_HEADLINES_API_KEY=, VAR_HEADLINES_SECTION=world]</swiftbar.environment>

from collections import namedtuple, OrderedDict
from swiftbar import images, request, util
from swiftbar.plugin import Plugin
from typing import Any, List

def get_valid_sections(api_key: str=None) -> List[str]:
    sections = []
    response, data, _ = request.swiftbar_request(
        host='content.guardianapis.com',
        path='/sections',
        query={
            'api-key': api_key,
        },
        return_type='json',
    )
    if response.status == 200 and data:
         return [item['id'] for item in data['response']['results'] if item['id'] != 'about']

    return sections

def main() -> None:
    plugin = Plugin()
    plugin.defaults_dict = OrderedDict()
    plugin.defaults_dict['DEBUG_ENABLED'] = {
        'default_value': False,
        'valid_values': [True, False],
        'type': bool,
        'setting_configuration': {
            'default': False,
            'flag': '--debug',
            'title': 'the "Debugging" menu',
        },
    }
    plugin.defaults_dict['VAR_HEADLINES_LIMIT'] = {
        'default_value': 30,
        'minmax': namedtuple('minmax', ['min', 'max'])(5, 50),
        'type': int,
        'setting_configuration': {
            'default': None,
            'flag': '--limit',
            'increment': 5,
            'title': 'Limit',
        },
    }
    plugin.defaults_dict['VAR_HEADLINES_API_KEY'] = {
        'default_value': None,
        'type': str,
    }
    plugin.defaults_dict['VAR_HEADLINES_SECTION'] = {
        'default_value': 'world',
        'type': str,
        'setting_configuration': {
            'default': None,
            'flag': '--section',
            'title': 'Section',
        },
    }
    # plugin.defaults_dict['VAR_HEADLINES_EDITION'] = {
    #     'default_value': 'us',
    #     'valid_values': sorted(['us', 'uk', 'international', 'au']),
    #     # 'valid_values': get_valid_sections(api_key=plugin.configuration['VAR_HEADLINES_API_KEY']),
    #     'type': str,
    #     'setting_configuration': {
    #         'default': None,
    #         'flag': '--edition',
    #         'title': 'Edition',
    #     },
    # }

    plugin.read_config()
    plugin.generate_args()
    plugin.update_json_from_args()

    valid_sections = get_valid_sections(api_key=plugin.configuration['VAR_HEADLINES_API_KEY'])
    if len(valid_sections) == 0:
         print('cannot get a list of sections')
         exit(1)
    
    plugin.defaults_dict['VAR_HEADLINES_SECTION']['valid_values'] = valid_sections

    response, data, _ = request.swiftbar_request(
         host='content.guardianapis.com',
         path='/search',
         query={
                'section': plugin.configuration['VAR_HEADLINES_SECTION'],
                # 'edition':  plugin.configuration['VAR_HEADLINES_EDITION'],
                'api-key': plugin.configuration['VAR_HEADLINES_API_KEY'],
                'page-size': plugin.configuration['VAR_HEADLINES_LIMIT'],
                'format': 'json',
         },
         return_type='json',
    )
    if response.status == 200 and data:
        if len(data['response']['results']) > 0:
            plugin.print_menu_title(f'Headlines: {len(data["response"]["results"])} in {data["response"]["results"][0]["sectionName"]}')
            for article in data['response']['results']:
                plugin.print_menu_item(
                     f'{util.prettify_timestamp(article["webPublicationDate"]).ljust(22)}{article["webTitle"].replace("|", "-")}',
                     color='blue' if plugin.invoked_by == 'xbar' else 'black',
                     limit=125,
                     href=article['webUrl'],
                     sfimage='link',
                     sfsize=8,
                     trim=False,
                )
        else:
            plugin.print_menu_title(f'Headlines: {len(data["response"]["results"])}')
    plugin.render_footer()
    
if __name__ == '__main__':
    main()
