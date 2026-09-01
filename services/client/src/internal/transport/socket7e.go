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
func (s *Socket7E) send(bytes []byte) (int, error) {
	if err := safe_socket.SendAll(s.socket, bytes); err != nil {
		return 0, err
	}

	return len(bytes), nil
}

func (s *Socket7E) sendHeader(bytes []byte) (int, error) {
	if _, err := s.send(MAGIC_NUMBER); err != nil {
		return 0, err
	}

	return s.send(bytes)
}

func (s *Socket7E) sendPayload(bytes []byte) (int, error) {
	return s.send(bytes)
}

func (s *Socket7E) ReadUntilHeaderFound() ([]byte, error) {
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

	headerFields, err := s.recv(int(headerSizeBytes[0]) + 1) // +1 para el agency_id
	if err != nil {
		return nil, err
	}

	return headerFields, nil
}

func (s *Socket7E) ReadPayload(size int) ([]byte, error) {
	return s.recv(size)
}

func (s *Socket7E) Send(header []byte, payload []byte) (int, error) {
	h, err := s.sendHeader(header)
	if err != nil {
		return 0, err
	}

	p, err := s.sendPayload(payload)
	if err != nil {
		return h, err
	}

	return h + p, nil
}

// Cierra la conexión TCP con el cliente
func (s *Socket7E) Close() error {
	return s.socket.Close()
}
