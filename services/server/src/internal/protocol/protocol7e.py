
from enum import Enum
from dataclasses import dataclass, fields
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

class Protocol7E:

    def parse_header(self):
        pass

    def build_header(self, size_payload: int, agency_id: int):
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

    def parse_payload(self):
        pass

    def build_payload(self, message_type: MessageType, bets: list[Bet]) -> list[bytes,int]:
        bytes = b""
        type_payload = message_type.value.to_bytes(1, byteorder='big')
        bytes += type_payload 

        for bet in bets:
            # Aquí se construye el payload con los datos de cada apuesta
            bet_bytes = b""
            # iterar sobre los datos de Bet distintos de null
            for field in fields(bet):
                data = getattr(bet, field.name)
                if data is not None and field.name != "agency_id":
                    data_type = BetDataType[field.name.upper()].to_bytes(1, byteorder='big')
                    data_length = max(1, (data.bit_length() + 7) // 8)
                    data_length_bytes = data_length.to_bytes(1, byteorder='big')
                    data_bytes = data.to_bytes(data_length, byteorder='big')
                    bet_bytes += data_type + data_length_bytes + data_bytes
            bytes += bet_bytes

        return [bytes,len(bytes)]

    def decode_type(self):
        pass

    def decode_length(self):
        pass

    def decode_value(self):
        pass

    def encode_type(self):
        pass

    def encode_length(self):
        pass

    def encode_value(self):
        pass

    def encode(self):
        pass

    def decode(self):
        pass