from argparse import ArgumentParser
import logging
import zmq
from .server import run_session
from RPiCamInterface import Message, MessageType
from typing import Optional

parser = ArgumentParser()
parser.add_argument('server_port', type=int, help='port on which the socket should bind')
parser.add_argument('control_port', type=int, help='port on which the socket should bind')
parser.add_argument('-n_threads', type=int, default='1', help='number of threads on which server should be running')
parser.add_argument('-log_level', type=str, default='error', help='info, error or fatal')

args = parser.parse_args()
ll = args.log_level.upper()
assert (ll in dir(logging)) and isinstance(getattr(logging, ll), int)
logging.basicConfig(level=getattr(logging, ll))

context = zmq.Context()

# socket for controling server 
control_sock: zmq.Socket = context.socket(zmq.REP) 
control_addr: str = f"tcp://*:{args.control_port}"
logging.info(f"binding control socket to {control_addr}")
control_sock.bind(control_addr)

session_id: str = ""

while True:
    msg = Message.from_bytes(control_sock.recv())
    if msg.payload != "begin session":
        continue
    session_id = msg.session_id
    if run_session(context, args.server_port, control_sock, session_id, args.n_threads):
        logging.info(f"terminating server from session id {session_id}")
        break
    control_sock.send_string(f"terminating session {session_id}")
    logging.info(f"terminating session {session_id}")
    
control_sock.close()
context.destroy()