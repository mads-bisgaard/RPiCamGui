
import logging
import zmq
import msgpack
import threading
from RPiCamInterface import Message, MessageType

def request_handler(context: zmq.Context, work_url: str, control_url: str):
    """
    Fcn which handles requests coming from the server entrypoint
    Args:
        url (str): address to which socket should connect
        port (int): port number to which socket should connect
    """
    work_sock = context.socket(zmq.REP)
    logging.info(f"connecting request handler work socket on thread {threading.current_thread().ident}")
    work_sock.connect(work_url)
    
    control_sock: zmq.Socket = context.socket(zmq.PULL)
    control_sock.connect(control_url)    
    
    poller = zmq.Poller()
    poller.register(work_sock, zmq.POLLIN)
    poller.register(control_sock, zmq.POLLIN)
    
    while True:
        
        try:
            socks = dict(poller.poll())
        except KeyboardInterrupt:
            break

        if control_sock in socks:
            break                
        if work_sock in socks:
            msg = work_sock.recv()
            # handle requests here
            work_sock.send(msg)

        
    logging.info(f'terminating thread {threading.current_thread().ident}')
    work_sock.close()
    control_sock.close()