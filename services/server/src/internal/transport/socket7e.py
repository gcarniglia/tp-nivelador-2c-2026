import socket

from services.server.src import safe_socket


class Socket7E:

    MAGIC_NUMBER = b'\x7E'

    def __init__(self, socket: socket.socket):
        self.__socket = socket

    ''' Recibe la cantidad especificada de bytes del socket'''
    def __recv(self, size: int) -> bytes:
        return safe_socket.recv_all(self.__socket, size)

    ''' Envía todos los bytes especificados al socket'''
    def __send(self, bytes: bytes) -> int:
        return safe_socket.send_all(self.__socket, bytes)

    def __send_header(self, bytes: bytes) -> int:
        self.__send(self.MAGIC_NUMBER)
        return self.__send(bytes)

    def __send_payload(self, bytes: bytes) -> int:
        return self.__send(bytes)

    def read_until_header_found(self) -> bytes:
        while True:
            byte = self.__recv(1)
            if byte == self.MAGIC_NUMBER:
                break
        header_size_bytes = self.__recv(1)
        header_fields = self.__recv(header_size_bytes[0] + 1)  # +1 para el agency_id
        return header_fields

    def read_payload(self, size: int) -> bytes:
        return self.__recv(size)

    def send(self, header: bytes, payload: bytes) -> int:
        h = self.__send_header(header)
        p = self.__send_payload(payload)
        return h + p

    ''' Cierra la conexión TCP con el cliente'''
    def close(self) -> None:
        self.__socket.close()