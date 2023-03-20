# Defined the message interface

from enum import IntEnum
from typing import Any, Optional, Dict, Union
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

class RequestPayload:
    def __init__(self, d: Dict = {}):
        if d == {}:
            d = {"options": {}}
        assert "options" in d, "'options' was not in the dict"
        self._content = {"options": {}}
    
    @property
    def options(self) -> Dict:
        return self._content["options"]
    
    @options.setter
    def options(self, opts: Dict):
        self._content["options"] = opts
        
class ReceivePayload:
    def __init__(self, d: Dict = {}):
        if d == {}:
            d = {"exitcode": True, "msg": "Dummy message"}
        assert "exitcode" in d, "'exitcode' was not in the dict"
        assert "msg" in d, "'msg' was not in the dict"
        self._content = d
    
    @property
    def exitcode(self) -> ExitCode:
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
        msg: Any = msgpack.unpackb(b)
        result: Message = Message()
        assert isinstance(msg, dict), 'received invalid bytes for creating Message'
        assert 'type' in msg, 'could not determine message type'
        result.type = msg['type']
        if 'payload' in msg:
            result._content["payload"] = msg['payload']
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
    def payload(self) -> Union[ReceivePayload, RequestPayload]:
        if "exitcode" in self._content['payload']:
            return ReceivePayload(self._content['payload'])
        else:
            return RequestPayload(self._content['payload'])
    
    @payload.setter
    def payload(self, p: Union[ReceivePayload, RequestPayload]) -> None:
        self._content['payload'] = p._content
        
    @property
    def session_id(self) -> Optional[UUID]:
        if isinstance(self._content['session_id'], str):
            return UUID(self._content['session_id'])
        return None
    
    @session_id.setter
    def session_id(self, value: Optional[UUID]) -> None:
        self._content['session_id'] = None if value is None else str(value)
        
    def to_bytes(self) -> Any:
        return msgpack.packb(self._content)
    
        
    