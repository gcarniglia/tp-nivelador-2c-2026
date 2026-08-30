package safe_socket

import (
	"errors"
	"io"
)

func SendAll(socket io.Writer, data []byte) error {
	totalBytesSent := 0

	for totalBytesSent < len(data) {
		sentBytes, err := socket.Write(data[totalBytesSent:])
		if err != nil {
			return err
		}

		totalBytesSent += sentBytes
	}

	return nil
}

func RecvAll(socket io.Reader, size int) ([]byte, error) {
	data := []byte{}

	for len(data) < size {
		buff := make([]byte, size-len(data))

		receivedBytes, err := socket.Read(buff)
		if err != nil {
			return nil, err
		}

		if receivedBytes == 0 {
			return nil, errors.New("socket closed before receiving all data")
		}

		data = append(data, buff[:receivedBytes]...)
	}

	return data, nil
}
