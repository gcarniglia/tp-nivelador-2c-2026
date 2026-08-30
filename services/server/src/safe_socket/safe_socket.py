import socket

def recv_all(socket: socket.socket, size: int):
    data = b""
    while len(data) < size:
        received_bytes = socket.recv(size - len(data))
        if not received_bytes: raise ConnectionError("Socket closed before receiving all data")
        data += received_bytes
    return data


def send_all(socket: socket.socket, bytes: bytes):
    total_bytes_sent = 0
    while total_bytes_sent < len(bytes):
        sent_bytes = socket.send(bytes[total_bytes_sent:])
        total_bytes_sent += sent_bytes
    return total_bytes_sent
