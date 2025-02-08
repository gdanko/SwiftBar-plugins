from swiftbar import util, request
from typing import Any, Dict, List, Union
import time

# https://financeapi.net/

def _get_valid_ranges() -> List[str]:
    return ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

def _get_valid_languages() -> List[str]:
    return ['en', 'fr', 'de', 'it', 'es', 'zh']

def _get_valid_regions() -> List[str]:
    return ['US', 'AU', 'CA', 'FR', 'DE', 'HK', 'IT', 'ES', 'GB', 'IN']

def _get_valid_quote_summary_modules() -> List[str]:
    return ['assetProfile', 'balanceSheetHistory', 'balanceSheetHistory', 'balanceSheetHistoryQuarterly', 'calendarEvents', 'cashflowStatementHistory', 'cashflowStatementHistory', 'cashflowStatementHistoryQuarterly', 'defaultKeyStatistics', 'earnings', 'earningsHistory', 'earningsTrend', 'esgScores', 'financialData', 'fundOwnership', 'fundProfile', 'incomeStatementHistory', 'incomeStatementHistoryQuarterly', 'indexTrend', 'insiderHolders', 'insiderTransactions', 'institutionOwnership', 'majorDirectHolders', 'majorHoldersBreakdown', 'netSharePurchaseActivity', 'price', 'quoteType', 'recommendationTrend', 'secFilings', 'sectorTrend', 'summaryDetail', 'upgradeDowngradeHistory']

def get_cookie_and_crumb():
    response, _, _ = request.swiftbar_request(
        host='fc.yahoo.com',
    )
    cookie = next((h[1] for h in response.headers.items() if h[0] == 'Set-Cookie'), None)
    if not cookie:
        return None, None

    response, crumb, err = request.swiftbar_request(
        host='query2.finance.yahoo.com',
        path='/v1/test/getcrumb',
        headers={'Cookie': cookie, 'User-Agent': request.get_useragent()},
        return_type='text',
    )
    if response.status == 200 and crumb:
        return cookie, crumb
    else:
        return None, None

def get_options(crumb: str=None, cookie: str=None, symbol: str=None, date:int =int(time.time())):
    headers = {'Cookie': cookie, 'User-Agent': request.get_useragent()}
    response, output, _ = request.swiftbar_request(
        host='query2.finance.yahoo.com',
        path=f'/v7/finance/options/{symbol}',
        query={
            'crumb': crumb,
            'symbol': symbol,
        },
        headers=headers,
        return_type='json',
    )
    if response.status == 200 and output:
        return output
    else:
        return None

def get_spark_data(crumb: str=None, cookie: str=None, symbols: List[str]=None, interval:str = '1d', range: str='1d'):
    headers = {'Cookie': cookie, 'User-Agent': request.get_useragent()}
    response, output, _ = request.swiftbar_request(
        host='query1.finance.yahoo.com',
        path=f'/v7/finance/spark',
        query={
            'crumb': crumb,
            'interval': interval,
            'range': range,
            'symbols': ','.join(symbols),
        },
        headers=headers,
        return_type='json',
    )
    if response.status == 200 and output:
        return output
    else:
        return None

def get_quote_summary(crumb: str=None, cookie: str=None, symbol: str=None, lang: str='en', region: str='US', modules: List[str]=None):
    headers = {'Cookie': cookie, 'User-Agent': request.get_useragent()}
    response, output, _ = request.swiftbar_request(
        host='query2.finance.yahoo.com',
        path=f'/v10/finance/quoteSummary/{symbol}',
        query={
            'corsDomain': 'finance.yahoo.com',
            'crumb': crumb,
            'formatted': False,
            'lang': lang,
            'modules': ','.join(modules),
            'region': region,
            'symbol': symbol,
        },
        headers=headers,
        return_type='json',
    )                
    if response.status == 200 and output:
        info = output['quoteSummary']['result'][0]
        company_data = {}
        for module in modules:
            for k, v in info[module].items():
                company_data[k] = v
        return company_data
    else:
        return None

def get_chart(crumb: str=None, cookie: str=None, ticker: str=None, interval:str = '1d', range: str='1d', lang: str='en', region: str='US', comparisons: List[str]=[]):
    headers = {'Cookie': cookie, 'User-Agent': request.get_useragent()}
    response, output, _ = request.swiftbar_request(
        host='query2.finance.yahoo.com',
        path=f'/v8/finance/chart/{ticker}',
        query={
            'comparisons': ','.join(comparisons),
            'crumb': crumb,
            'events': 'div,splits,capitalGains',
            'includePrePost': False,
            'interval': interval,
            'lang': lang,
            'range': range,
            'region': region,
        },
        headers=headers,
        return_type='json',
    )                
    if response.status == 200 and output:
        return output
    else:
        return None
    
# /v6/finance/recommendationsbysymbol/{symbol}

def get_market_summary(crumb: str=None, cookie: str=None, lang: str='en', region: str='US'):
    headers = {'Cookie': cookie, 'User-Agent': request.get_useragent()}
    response, output, _ = request.swiftbar_request(
        host='query2.finance.yahoo.com',
        path=f'/v6/finance/quote/marketSummary',
        query={
            'crumb': crumb,
            'lang': lang,
            'region': region,
        },
        headers=headers,
        return_type='json',
    )                
    if response.status == 200 and output:
        return output
    else:
        return None

def get_trending(crumb: str=None, cookie: str=None, region: str='US'):
    headers = {'Cookie': cookie, 'User-Agent': request.get_useragent()}
    response, output, _ = request.swiftbar_request(
        host='query1.finance.yahoo.com',
        path=f'/v1/finance/trending/{region}',
        query={
            'crumb': crumb,
        },
        headers=headers,
        return_type='json',
    )                
    if response.status == 200 and output:
        return output
    else:
        return None
