import json
from types import SimpleNamespace

from gevent import socket, ssl, sleep


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
            for key, value in obj.items():
                obj[key] = namespacify(value)
            return SimpleNamespace(**obj)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = namespacify(item)
        return obj
    
    return namespacify(json_data)


def make_request(token: str, method: str, body=None) -> SimpleNamespace:
    timeout = 5
    request_url = api_url.format(method=method, token=token)
    host = api_url[8:api_url.find('/bot')]
    path = request_url[request_url.find('/bot'):]
    s = f'POST {path} HTTP/1.1\r\n'
    s += f'Host: {host}\r\n'
    
    if body is not None:
        body_data = json.dumps(body)
        s += f'Content-Length: {len(body_data)}\r\n'
        s += 'Content-Type: application/json; charset=utf-8\r\n'
        if 'timeout' in body:
            timeout += body['timeout']
    else:
        body_data = ''
    
    s += f'\r\n'
    s += body_data
    with socket.create_connection((host, 443)) as tcp_socket:
        with ssl.wrap_socket(tcp_socket) as ssl_socket:
            ssl_socket.send(s.encode())
            data: bytes = ssl_socket.recv(1024*7000)
            headers, body = data.split(b'\r\n'*2, maxsplit=1)
            decoded_data: SimpleNamespace = decode_json_body(body)
            if not decoded_data.ok:
                raise APIError(f'[{decoded_data.error_code}] {decoded_data.description}')
            return decoded_data
