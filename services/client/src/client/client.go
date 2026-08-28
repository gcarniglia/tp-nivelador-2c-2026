package client

import (
	"bufio"
	"net"
	"os"
	"time"

	"github.com/7574-sistemas-distribuidos/tp-nivelador/src/logger"
	"github.com/7574-sistemas-distribuidos/tp-nivelador/src/safe_socket"
)

const CONNECTION_ATTEMPTS_MAX = 3
const CONNECTION_ATTEMPS_DELAY_MS = 200

const ECHO_CLIENT_BUFFER_SIZE = 512

type ClientConfig struct {
	ServerHost             string
	ServerPort             string
	AgencyId               string
	InputFile              string
	OutputFile             string
	FileContainerDirectory string
}

type Client struct {
	conn   net.Conn
	config ClientConfig
}

func NewClient(config ClientConfig) (*Client, error) {
	conn, err := connectToServer(config.ServerHost, config.ServerPort)
	if err != nil {
		logger.Warn("connect-to-server", logger.Fail)
		return nil, err
	}

	client := &Client{conn: conn, config: config}
	return client, nil
}

func connectToServer(host, port string) (net.Conn, error) {
	const action = "connect-to-server"
	var err error
	var conn net.Conn

	logger.Info(action, logger.InProgress)
	for i := range CONNECTION_ATTEMPTS_MAX {
		conn, err = net.Dial("tcp", host+":"+port)
		if err != nil {
			logger.Warn(action, logger.Fail, "attempt", i)
			time.Sleep(CONNECTION_ATTEMPS_DELAY_MS * time.Millisecond)
			continue
		}

		logger.Info(action, logger.Success)
		break
	}

	return conn, err
}

func (client *Client) Run() error {
	const mainAction = "test-echo-server"
	defer client.conn.Close()

	outputFile, err := os.OpenFile(client.config.FileContainerDirectory+client.config.OutputFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		logger.Error(mainAction, logger.Fail)
		return err
	}
	defer outputFile.Close()

	inputFile, err := os.Open(client.config.FileContainerDirectory + client.config.InputFile)

	if err != nil {
		logger.Error("open-input-file", logger.Fail)
		return err
	}

	defer inputFile.Close()

	scanner := bufio.NewScanner(inputFile)

	for scanner.Scan() {
		line := scanner.Text()

		messageArgs := []any{"agency-id", client.config.AgencyId, "message", line}
		logger.Info(mainAction, logger.InProgress, messageArgs...)

		clientMessage := line

		if err := safe_socket.SendAll(client.conn, []byte(clientMessage)); err != nil {
			logger.Error("send-message", logger.Fail, messageArgs...)
			return err
		}

		responseBuffer, err := safe_socket.RecvAll(client.conn, ECHO_CLIENT_BUFFER_SIZE)
		if err != nil {
			logger.Error("recv-response", logger.Fail, messageArgs...)
			return err
		}

		if string(responseBuffer) == clientMessage {
			err := client.WriteOutputDataInFile(responseBuffer, outputFile)
			if err != nil {
				logger.Error("write-output-file", logger.Fail, messageArgs...)
				return err
			}
		} else {
			logger.Error("check-response", logger.Fail, messageArgs...)
			return err
		}

	}

	if err := scanner.Err(); err != nil {
		logger.Error("scan-input-file", logger.Fail)
		return err
	}

	logger.Info(mainAction, logger.Success, "agency-id", client.config.AgencyId)

	return nil
}

func (client *Client) WriteOutputDataInFile(responseBuffer []byte, outputFile *os.File) error {
	const mainAction = "write-output-file"

	writer := bufio.NewWriter(outputFile)
	if _, err := writer.WriteString(string(responseBuffer) + "\n"); err != nil {
		return err
	}

	if err := writer.Flush(); err != nil {
		return err
	}

	logger.Info(mainAction, logger.Success, "message", responseBuffer)
	return nil
}
