import socket
from protofire.utils.logger import create_log
from protofire.http.http import HttpRequest, HttpResponse

log = create_log('HANDLER', 'cyan')


def handle_request(client_socket: socket.socket, client_address: tuple):
    log(4, f'TREATING CONNECTION FROM {client_address[0]}:{client_address[1]} as HTTP request')

    request = client_socket.recv(4096)

    #print(str(request, 'ascii').replace('\\', '\\\\').replace('\r', '\\r').replace('\n', '\\n'))
    http_request = HttpRequest._from_str(str(request, 'ascii'))
    log(4, f'RECEIVED REQUEST:\n{http_request}')
