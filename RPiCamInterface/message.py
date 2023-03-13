# Defined the message interface

from enum import IntEnum
from typing import Any, Optional
import msgpack
import logging

class ExitCode(IntEnum):
    Success = 1
    Failure = 0

class MessageType(IntEnum):
    KILL_SERVER = 0
    BEGIN_SESSION = 1
    END_SESSION = 2
    COMMAND = 3
    

class Message:
    
    @staticmethod
    def from_bytes(b: bytes) -> Any:
        msg: Any = msgpack.unpackb(b)
        result: Message = Message()
        assert isinstance(msg, dict), 'received invalid bytes for creating Message'
        assert 'type' in msg, 'could not determine message type'
        result.type = msg['type']
        if 'payload' in msg:
            result.payload = msg['payload']
        if 'session_id' in msg:
            result.session_id = msg['session_id']
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
    def session_id(self) -> Optional[str]:
        return self._content['session_id']
    
    @session_id.setter
    def session_id(self, value: str) -> None:
        self._content['session_id'] = value
        
    def to_bytes(self) -> Any:
        return msgpack.packb(self._content)
    
        
    