from typing import Any, Dict, Optional, Union
import json
import http.client

def get_useragent() -> str:
    return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

def percent_encode(string: str=None) -> str:
    """
    Percent encode a string.
    """
    hex_digits = '0123456789ABCDEF'
    result = []
    for char in string:
        # Check if the character is unreserved (alphanumeric or -._~)
        if char.isalnum() or char in '-._~':
            result.append(char)
        else:
            # Convert the character to its percent-encoded form
            result.append(f'%{hex_digits[ord(char) >> 4]}{hex_digits[ord(char) & 0xF]}')
    return ''.join(result)

def encode_query_string(query: Dict[str, str]=None) -> str:
    """
    Encode a query string.
    """
    encoded_pairs = []
    for key, value in query.items():
        encoded_key = percent_encode(str(key))
        encoded_value = percent_encode(str(value))
        encoded_pairs.append(f"{encoded_key}={encoded_value}")
    return '&'.join(encoded_pairs)

def swiftbar_request(host: str=None, path: str='/', method: Optional[str]='GET', headers: Optional[Dict[str, Any]]=None, query: Optional[Dict[str, Any]]=None, encode_query: bool=False, data: Optional[Dict[str, Any]]=None, return_type: str='text') -> Union[int, str, bytes, Dict, Any, None]:
    """
    Handle HTTP basic requests.
    """
    # Add support for other methods
    response = None

    if query:
        if encode_query:
            params_str = encode_query_string(query)
        else:
            params_str = '&'.join([f'{k}={v}' for k, v in query.items()])
        path = '?'.join([path, params_str])

    conn = http.client.HTTPSConnection(host)
    if headers:
        conn.request(method, path, headers=headers)
    else:
        conn.request(method, path)
    response = conn.getresponse()
    content = response.read()
    
    if return_type == 'text':
        return response, content.decode(), None
    elif return_type == 'binary':
        return response, content, None
    elif return_type == 'json':
        try:
            json_body = json.loads(content.decode())
            return response, json_body, None
        except Exception as e:
            return response, None, e
    else:
        raise ValueError('Invalid return_type. Choose "json", "text", or "binary".')
