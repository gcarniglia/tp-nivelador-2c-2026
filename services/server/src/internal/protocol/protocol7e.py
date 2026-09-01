
from enum import Enum
from dataclasses import dataclass, fields
from services.server.src.internal.transport.socket7e import Socket7E
from services.server.src_frozen.lottery.bet import Bet


class MessageType(Enum):
    BET = 0x01
    BATCH = 0x02

class BetDataType(Enum):
    FIRST_NAME = 0X01
    LAST_NAME = 0X02
    DOCUMENT = 0X03
    BIRTHDATE = 0X04
    NUMBER = 0X05

@dataclass
class Message7E:
    
    type: MessageType
    bets: list[Bet]
    agency_id: int

class Protocol7E:

    QUANTITY_FIELDS_BET = len(fields(Bet)) - 1

    def __encode_header(self, size_payload: int, agency_id: int):
        bytes = b""
        size_payload_length = max(1, (size_payload.bit_length() + 7) // 8)
        size_payload_length_bytes = size_payload_length.to_bytes(1, byteorder='big')

        # size_payload_length > 255 es un escenario donde se exceden los 255 caracteres para representar
        # el tamaño del payload, lo cual no es soportado por el protocolo. Ocurre en 2^2040 - 1,
        # que es un número mucho mayor que los atomos en el universo observable

        size_payload_bytes = size_payload.to_bytes(size_payload_length, byteorder='big')
        agency_id_bytes = agency_id.to_bytes(1, byteorder='big')

        bytes += size_payload_length_bytes + size_payload_bytes + agency_id_bytes
        return bytes

    def __encode_bet_field_data(self, field_name: str, data) -> tuple[bytes, bytes, bytes]:
        if data is not None and field_name != "agency_id":
            data_type = BetDataType[field_name.upper()].to_bytes(1, byteorder="big")

            if isinstance(data, str):
                data_bytes = data.encode("utf-8")
            elif isinstance(data, int):
                data_length = max(1, (data.bit_length() + 7) // 8)
                data_bytes = data.to_bytes(data_length, byteorder="big")
            else:
                raise TypeError(f"Tipo no soportado: {type(data)}")
            
        data_length_bytes = len(data_bytes).to_bytes(1, byteorder="big")
        return data_type, data_length_bytes, data_bytes


    def __encode_payload(self, message_type: MessageType, bets: list[Bet]) -> list[bytes,int]:
        bytes = b""
        type_payload = message_type.value.to_bytes(1, byteorder='big')
        bytes += type_payload 

        for bet in bets:
            # Aquí se construye el payload con los datos de cada apuesta
            bet_bytes = b""
            # iterar sobre los datos de Bet distintos de null
            for field in fields(bet):
                data = getattr(bet, field.name)
                data_type,data_length_bytes,data_bytes = self.__encode_bet_field_data(field.name, data)
                bet_bytes += data_type + data_length_bytes + data_bytes

            bytes += bet_bytes

        return [bytes,len(bytes)]

    def __decode_header(self, header: bytes) -> tuple[int,int]:
        return header[:-1],header[-1]

    def encode(self, message: Message7E) -> tuple[bytes,bytes]:
        payload, size_payload = self.__encode_payload(message.type, message.bets)
        header = self.__encode_header(size_payload, message.agency_id)
        return header,payload

    def __decode_bet_field_data(self, payload: bytes, agency_id: int, index: int) -> tuple[Bet,int]:
        bet = Bet()
        for _ in range(self.QUANTITY_FIELDS_BET):
            if index >= len(payload):
                break #Escenario no posible porque no hay problema de integridad de data

            data_type = BetDataType(int.from_bytes(payload[index:index+1], byteorder='big'))
            index += 1
            data_length = int.from_bytes(payload[index:index+1], byteorder='big')
            index += 1
            data_bytes = payload[index:index+data_length]
            index += data_length

            if data_type == BetDataType.FIRST_NAME:
                bet.first_name = data_bytes.decode("utf-8")
            elif data_type == BetDataType.LAST_NAME:
                bet.last_name = data_bytes.decode("utf-8")
            elif data_type == BetDataType.DOCUMENT:
                bet.document = int.from_bytes(data_bytes, byteorder='big')
            elif data_type == BetDataType.BIRTHDATE:
                bet.birthdate = int.from_bytes(data_bytes, byteorder='big')
            elif data_type == BetDataType.NUMBER:
                bet.number = int.from_bytes(data_bytes, byteorder='big')
        return bet,index
        
    def __decode(self, payload: bytes, agency_id: int) -> Message7E:
        mensaje = Message7E()
        mensaje.agency_id = agency_id
        mensaje.type = MessageType(int.from_bytes(payload[0:1], byteorder='big'))
        mensaje.bets = []
        index = 1
        while index < len(payload):
            bet,index = self.__decode_bet_field_data(payload,agency_id,index)
            mensaje.bets.append(bet)
        return mensaje

    def write_message(self, connection: Socket7E, message: Message7E):
        header,payload = self.encode(message)
        connection.send(header, payload)

    def read_message(self, connection: Socket7E) -> Message7E:
        header = connection.read_until_header_found()

        size_payload,agency_id = self.__decode_header(header)
        payload = connection.read_payload(size_payload)
        message = self.__decode(payload, agency_id)
        return message

