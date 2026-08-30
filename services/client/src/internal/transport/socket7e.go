package transport

import (
	"net"

	"github.com/7574-sistemas-distribuidos/tp-nivelador/src/safe_socket"
)

type Socket7E struct {
	socket net.Conn
}

var MAGIC_NUMBER = []byte{0x7E}

func NewSocket7E(socket net.Conn) *Socket7E {
	return &Socket7E{
		socket: socket,
	}
}

// Recibe la cantidad especificada de bytes del socket
func (s *Socket7E) recv(size int) ([]byte, error) {
	return safe_socket.RecvAll(s.socket, size)
}

// Envía todos los bytes especificados al socket
func (s *Socket7E) send(bytes []byte) error {
	return safe_socket.SendAll(s.socket, bytes)
}

// Devuelve los campos del header
func (s *Socket7E) ReadHeader() ([]byte, error) {
	for {
		b, err := s.recv(1)
		if err != nil {
			return nil, err
		}

		if b[0] == MAGIC_NUMBER[0] {
			break
		}
	}

	headerSizeBytes, err := s.recv(1)
	if err != nil {
		return nil, err
	}

	headerFields, err := s.recv(int(headerSizeBytes[0]))
	if err != nil {
		return nil, err
	}

	return headerFields, nil
}

func (s *Socket7E) ReadPayload(size int) ([]byte, error) {
	return s.recv(size)
}

func (s *Socket7E) SendHeader(bytes []byte) error {
	if err := s.send(MAGIC_NUMBER); err != nil {
		return err
	}

	return s.send(bytes)
}

func (s *Socket7E) SendPayload(bytes []byte) error {
	return s.send(bytes)
}

// Cierra la conexión TCP con el cliente
func (s *Socket7E) Close() error {
	return s.socket.Close()
}
