import json
from types import SimpleNamespace

import errno
from gevent import socket, ssl, sleep

from .util import greenlet


api_url = 'https://api.telegram.org/bot{token}/{method}'


class APIError(Exception): pass


def decode_json_body(body: bytes) -> SimpleNamespace:
    try:
        json_data = json.loads(body.decode())
    except json.decoder.JSONDecodeError:
        print(body)
        return SimpleNamespace()

    def namespacify(obj):
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if key == 'from':
                    obj['from_user'] = namespacify(obj.pop('from'))
                    continue
                obj[key] = namespacify(value)
            return SimpleNamespace(**obj)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = namespacify(item)
        return obj
    
    return namespacify(json_data)


@greenlet
def make_request(token: str, method: str, body=None) -> SimpleNamespace:
    request_url = api_url.format(method=method, token=token)
    host = api_url[8:api_url.find('/bot')]
    path = request_url[request_url.find('/bot'):]
    request = f'POST {path} HTTP/1.1\r\n'
    request += f'Host: {host}\r\n'
    
    if body is not None:
        body_data = json.dumps(body)
        request += f'Content-Length: {len(body_data)}\r\n'
        request += 'Content-Type: application/json; charset=utf-8\r\n'
    else:
        body_data = ''
    
    request += f'\r\n'
    request += body_data
    
    with socket.create_connection((host, 443)) as tcp_socket:
        with ssl.wrap_socket(tcp_socket) as ssl_socket:
            ssl_socket.sendall(request.encode())
            data: bytes = b''
            
            # Reading headers
            while True:
                data += ssl_socket.recv(256)
                if b'\r\n\r\n' in data:
                    break
            headers, body = data.split(b'\r\n\r\n', maxsplit=1)
            
            # Get content-length
            content_length = 0
            for i in headers.decode().split('\r\n'):
                if ':' not in i:
                    continue
                header_name, value = i.split(':', maxsplit=1)
                if header_name.lower().strip() == 'content-length':
                    content_length = int(value.strip())
                    break
            
            # Read the rest of the body
            data_left = content_length - len(body)
            if  data_left > 0:
                body += ssl_socket.recv(data_left)
            
            decoded_data: SimpleNamespace = decode_json_body(body)
            if not decoded_data.ok:
                code = decoded_data.error_code
                descr = decoded_data.description
                raise APIError(f'''[{code}] {descr}''')
            return decoded_data
