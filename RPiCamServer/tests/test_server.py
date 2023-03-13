
import pytest
import subprocess
import sys
import os
from pathlib import Path
from RPiCamInterface import Message, MessageType, ExitCode
import zmq

_PROJECT_ROOT = Path(__file__).parent.parent.parent

@pytest.fixture
def server_data():
    port: int = 1234
    nthreads: int = 1
    proc: subprocess.Popen = subprocess.Popen([sys.executable, '-m', 'RPiCamServer', str(port), '-n_threads', str(nthreads)], cwd=_PROJECT_ROOT)
    yield proc, port
    proc.kill()

@pytest.fixture
def client_socket(server_data):
    _, port = server_data
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)
    try:
        req_socket.connect(f"tcp://localhost:{port}")
    except:
        raise Exception('Could not connect client socket to server in client_socket test fixture')
    yield req_socket
    req_socket.close()
    context.destroy()
    
def test_start_signal(client_socket: zmq.Socket):
    """
    Check that server accepts start signal
    """
    msg = Message()
    msg.type = MessageType.BEGIN_SESSION
    msg.payload = {}
    print(msg.to_bytes())
    client_socket.send(msg.to_bytes())
    response = Message.from_bytes(client_socket.recv())
    assert response.type == MessageType.BEGIN_SESSION, 'Client did not receive BEGIN_SESSION type after initial request'
    assert response.payload['exitcode'] == ExitCode.Success, 'Could not initiate session on server side'
    assert isinstance(response.session_id, str), 'Did not reveice session_id'
    
    
