# Defined the message interface

from enum import IntEnum
from typing import Any
import msgpack
import logging


class MessageType(IntEnum):
    KILL_SERVER = 0
    BEGIN_SESSION = 1
    END_SESSION = 2
    

class Message:
    
    @staticmethod
    def from_bytes(b: bytes) -> Any:
        msg: Any = msgpack.unpackb(b)
        result: Message = Message()
        assert isinstance(msg, dict), 'received invalid bytes for creating Message'
        assert 'type' in msg, 'could not determine message type'
        result.type = msg['type']
        assert 'payload' in msg, 'could not determine message payload'
        result.payload = msg['payload']
        return result
        
    def __init__(self):
        self._content = dict()
    
    @property
    def type(self) -> MessageType:
        return MessageType(self._content['type'])
    
    @type.setter
    def type(self, t: MessageType) -> None:
        self._content['type'] = int(t)
        
    @property
    def payload(self) -> Any:
        return self._content['payload']
    
    @payload.setter
    def payload(self, p: Any) -> None:
        self._content['payload'] = p
        
    @property
    def session_id(self) -> str:
        return self._content['session_id']
    
    @session_id.setter
    def session_id(self, value: str) -> None:
        self._content['session_id'] = value
        
    def to_bytes(self) -> Any:
        return msgpack.packb(self._content)
    
        
    