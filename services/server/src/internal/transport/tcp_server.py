import socket
from services.server.src.internal.transport.socket7e import Socket7E


class TcpServer:
        
    '''Se crea y configura el socket del servidor TCP,
    listo para aceptar conexiones entrantes'''
    def __init__(self, port: int, listen_backlog: int):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(("", port))
        self._server_socket.listen(listen_backlog)

    '''Bloquea hasta que se acepte una nueva conexión TCP entrante,
    retornando un objeto TcpConnection y la dirección del cliente'''
    def accept(self):
        client_sock, addr = self._server_socket.accept()
        return Socket7E(client_sock), addr

    ''' Cierra el socket del servidor'''
    def close(self) -> None:
        self._server_socket.close()
