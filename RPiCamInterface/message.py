# Defined the message interface

from enum import IntEnum
from typing import Any, Optional, Dict, Union, List
import msgpack
from uuid import UUID

class ExitCode(IntEnum):
    Success = 1
    Failure = 0

class MessageType(IntEnum):
    KILL_SERVER = 0
    BEGIN_SESSION = 1
    END_SESSION = 2
    COMMAND = 3

class Payload:
    pass

class RequestPayload(Payload):
    def __init__(self, d: Dict = {}):
        self._keys: List[str] = ['options']
        if d == {}:
            self._content = {}
            for key in self._keys:
                self._content[key] = None
        else:
            self._content = d
    
    @property
    def options(self) -> Optional[Dict]:
        return self._content['options']
    
    @options.setter
    def options(self, opts: Dict):
        self._content['options'] = opts
        
class ReceivePayload(Payload):
    def __init__(self, d: Dict = {}):
        self._keys: List[str] = ['exitcode', 'msg']
        if d == {}:
            self._content = {}
            for key in self._keys:
                self._content[key] = None
        else:
            self._content = d
    
    @property
    def exitcode(self) -> Optional[ExitCode]:
        return self._content["exitcode"]
    
    @exitcode.setter
    def exitcode(self, ec: ExitCode) -> None:
        self._content["exitcode"] = ec
    
    @property
    def msg(self) -> str:
        return self._content["msg"]
    
    @msg.setter
    def msg(self, m: str) -> None:
        self._content["msg"] = m
    
class Message:
    
    @staticmethod
    def from_bytes(b: bytes) -> Any:
        try:
            msg: Any = msgpack.unpackb(b)
        except:
            raise ValueError('received invalid bytes for creating Message')
        result: Message = Message()
        assert isinstance(msg, dict), 'received invalid bytes for creating Message'
        for key in result._keys:
            if key in msg:
                result._content[key] = msg[key]
        return result
        
    def __init__(self):
        self._keys: List[str] = ['type', 'payload', 'payload_type', 'session_id']
        self._content = dict()
        for key in self._keys:
            self._content[key] = None
    
    @property
    def type(self) -> Optional[MessageType]:
        try:
            return MessageType(self._content['type'])
        except:
            return None
    
    @type.setter
    def type(self, t: MessageType) -> None:
        self._content['type'] = int(t)
        
    @property
    def payload(self) -> Optional[Union[ReceivePayload, RequestPayload]]:
        try:
            return globals()[self._content['payload_type']](self._content['payload'])
        except:
            return None
    
    @payload.setter
    def payload(self, p: Union[ReceivePayload, RequestPayload]) -> None:
        self._content['payload_type'] = type(p).__name__
        self._content['payload'] = p._content
        
    @property
    def session_id(self) -> Optional[UUID]:
        try:
            return UUID(self._content['session_id'])
        except:
            return None
    
    @session_id.setter
    def session_id(self, value: Optional[UUID]) -> None:
        self._content['session_id'] = None if value is None else str(value)
        
    def to_bytes(self) -> Any:
        return msgpack.packb(self._content)
    
        
    