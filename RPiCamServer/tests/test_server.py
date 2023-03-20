
import pytest
import subprocess
import sys
from pathlib import Path
from RPiCamInterface import Message, MessageType, ExitCode, RequestPayload
import zmq
from uuid import uuid1, UUID


_PROJECT_ROOT = Path(__file__).parent.parent.parent

@pytest.fixture
def client_server_pair():
    port: int = 1234
    nthreads: int = 1
    proc: subprocess.Popen = subprocess.Popen([sys.executable, '-m', 'RPiCamServer', str(port), '-n_threads', str(nthreads)], cwd=_PROJECT_ROOT)
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)
    try:
        req_socket.connect(f"tcp://localhost:{port}")
    except:
        raise Exception('Could not connect client socket to server in client_socket test fixture')        
    yield proc, req_socket
    req_socket.close()
    context.destroy()
    proc.kill()

def test_start_signal(client_server_pair):
    """
    Check that server only accepts start signal at first message and returns session_id
    """
    _, client_socket = client_server_pair
    msg = Message()
    msg.payload = RequestPayload()
    
    msg.type = MessageType.COMMAND
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.payload.exitcode == ExitCode.Failure

    msg.type = MessageType.END_SESSION
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.payload.exitcode == ExitCode.Failure

    msg.type = MessageType.KILL_SERVER
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.payload.exitcode == ExitCode.Failure

    msg.type = MessageType.BEGIN_SESSION
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.payload.exitcode == ExitCode.Success
    assert response.type == MessageType.BEGIN_SESSION, 'Client did not receive BEGIN_SESSION type after initial request'
    assert isinstance(response.session_id, UUID), 'Did not reveice session_id'
    
    
def test_session_id(client_server_pair):
    """
    Test that server fails if incorrect session_id is passed
    """
    _, client_socket = client_server_pair
    msg = Message()
    msg.payload = RequestPayload()
    msg.type = MessageType.BEGIN_SESSION
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.payload.exitcode == ExitCode.Success
    
    session_id = response.session_id
    bad_session_id = uuid1()
    msg = Message()
    msg.payload = RequestPayload()
    msg.type = MessageType.COMMAND
    msg.session_id = bad_session_id
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.payload.exitcode == ExitCode.Failure, "Server accepted invalid session id"
    
    msg.session_id = session_id
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.payload.exitcode == ExitCode.Success, "Server did not accept valid session id"    
    
