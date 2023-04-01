
import pytest
import subprocess
import sys
from pathlib import Path
from RPiCamInterface import Message, MessageType, ExitCode, RequestPayload
import zmq
from uuid import uuid1, UUID
from waiting import wait


_PROJECT_ROOT = Path(__file__).parent.parent.parent

@pytest.fixture
def client_server_pair():
    
    def send_receive(socket: zmq.Socket, msg: Message):
        socket.send(msg.to_bytes())
        return Message.from_bytes(socket.recv())
    
    port: int = 1234
    nthreads: int = 1
    proc: subprocess.Popen = subprocess.Popen([sys.executable, '-m', 'RPiCamServer', str(port), '-n_threads', str(nthreads)], cwd=_PROJECT_ROOT)
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)
    try:
        req_socket.connect(f"tcp://localhost:{port}")
        req_socket.setsockopt(zmq.RCVTIMEO, 2000) # timeout if no response after 2sec
    except:
        raise Exception('Could not connect client socket to server in client_socket test fixture')
    assert proc.poll() is None, "Server died unexpectedly"
    yield proc, lambda msg: send_receive(req_socket, msg)
    req_socket.close()
    context.destroy()
    proc.kill()

def test_start_signal(client_server_pair):
    """
    Check that server only accepts start signal at first message and returns session_id
    """
    _, send_receive = client_server_pair
    msg = Message()
    msg.payload = RequestPayload()
    
    msg.type = MessageType.COMMAND
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Failure

    msg.type = MessageType.END_SESSION
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Failure

    msg.type = MessageType.KILL_SERVER
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Failure

    msg.type = MessageType.BEGIN_SESSION
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Success
    assert response.type == MessageType.BEGIN_SESSION, 'Client did not receive BEGIN_SESSION type after initial request'
    assert isinstance(response.session_id, UUID), 'Did not reveice session_id'
    
    
def test_session_id(client_server_pair):
    """
    Test that server fails if incorrect session_id is passed
    """
    _, send_receive = client_server_pair
    msg = Message()
    msg.payload = RequestPayload()
    msg.type = MessageType.BEGIN_SESSION
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Success
    
    session_id = response.session_id
    bad_session_id = uuid1()
    msg = Message()
    msg.payload = RequestPayload()
    msg.type = MessageType.COMMAND
    msg.session_id = bad_session_id
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Failure, "Server accepted invalid session id"
    
    msg.session_id = session_id
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Success, "Server did not accept valid session id"    
    
    
def test_kill_server(client_server_pair):
    """
    Check that we can kill server
    """
    server_proc, send_receive = client_server_pair

    msg = Message()
    msg.payload = RequestPayload()
    msg.type = MessageType.KILL_SERVER
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Failure
    
    msg.type = MessageType.BEGIN_SESSION
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Success
    
    msg.type = MessageType.KILL_SERVER
    msg.session_id = response.session_id
    response = send_receive(msg)
    assert response.payload.exitcode == ExitCode.Success
    
    try:
        wait(lambda: False if server_proc.poll() is None else True, timeout_seconds=5, waiting_for='server subprocess to die')    
    except TimeoutError:
        assert False, 'server subprocess did not die after attempting to terminate it'