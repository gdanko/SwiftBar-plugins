from typing import Any, Dict, Optional, Union
import json
import http.client
import re
import urllib.parse

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

def encode_query_string(params: Dict[str, str]=None) -> str:
    """
    Encode a query string.
    """
    encoded_pairs = []
    for key, value in params.items():
        encoded_key = percent_encode(str(key))
        encoded_value = percent_encode(str(value))
        encoded_pairs.append(f"{encoded_key}={encoded_value}")
    return '&'.join(encoded_pairs)

def swiftbar_request(url: str=None, method: Optional[str]='GET', headers: Optional[Dict[str, Any]]=None, query: Optional[Dict[str, Any]]=None, data: Optional[Dict[str, Any]]=None, return_type: str='text') -> Union[int, str, bytes, dict, None]:
    """
    Handle HTTP basic requests.
    """
    # Add support for other methods
    response = None
    parsed = urllib.parse.urlparse(url)

    host = parsed.hostname
    path = parsed.path

    if parsed.query:
        for k, v in dict(re.split(r'\s*=\s*', pair) for pair in re.split('&', parsed.query)).items():
            if not k in query:
                query[k] = v

    connection_string = path
    if query:
        connection_string = connection_string + '?' + encode_query_string(query)

    conn = http.client.HTTPSConnection(host)
    conn.request(method, connection_string)
    response = conn.getresponse()
    status_code = response.status
    content = response.read()
    
    if return_type == 'text':
        return status_code, content.decode(), None
    elif return_type == 'binary':
        return status_code, content, None
    elif return_type == 'json':
        try:
            json_body = json.loads(content.decode())
            return status_code, json_body, None
        except Exception as e:
            return status_code, None, e
    else:
        raise ValueError('Invalid return_type. Choose "json", "text", or "binary".')
