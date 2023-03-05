#!/bin/python

import zmq
import threading
import logging
from .handler import request_handler
from RPiCamInterface import Message, MessageType
import time
from typing import Optional




def proxy(frontend: zmq.Socket, backend: zmq.Socket, control: zmq.Socket, session_id: str) -> Optional[Message]:
    """
    Simple control proxy as the one provided directly by zmq (which doesn't work for some reason)
    """
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)
    poller.register(control, zmq.POLLIN)

    while True:
        try:
            socks = dict(poller.poll())
        except KeyboardInterrupt:
            return None
        if frontend in socks:
            msg_id, blank, msg = frontend.recv_multipart()
            if Message.from_bytes(msg).session_id == session_id:
                backend.send_multipart([msg_id, blank, msg])
        if backend in socks:
            frontend.send_multipart(backend.recv_multipart())
        if control in socks:
            msg = Message.from_bytes(control.recv())
            if msg.session_id == session_id:
                return Message.from_bytes(control.recv())
                

def run_session(context: zmq.Context, rout_port: int, control_sock: zmq.Socket, session_id: str, n_threads: int = 1) -> bool:
    """
    Server which should be running on Rpi
    """
    assert n_threads > 0, 'server requires at least one thread running a worker'
    
    # socket for receiving incomming requests
    rout_sock: zmq.Socket = context.socket(zmq.ROUTER) 
    rout_addr: str = f"tcp://*:{rout_port}"
    logging.info(f"binding router socket to {rout_addr}")
    rout_sock.bind(rout_addr)

    # socket for dealing requests to threads handling camera
    deal_sock: zmq.Socket = context.socket(zmq.DEALER)
    deal_addr: str = f"inproc://handlers_work"
    logging.info(f"binding deal socket to {deal_addr}")
    deal_sock.bind(deal_addr)
    
    # socket for killing handler threads
    pub_sock: zmq.Socket = context.socket(zmq.PUB)
    pub_addr: str = f"inproc://handlers_kill"
    logging.info(f"binding pub socket to {pub_addr}")
    pub_sock.bind(pub_addr)
    
    for _ in range(n_threads):
        thread = threading.Thread(target=request_handler, args=(context, deal_addr, pub_addr, session_id))
        thread.daemon = True
        thread.start()
    
    control_msg = proxy(rout_sock, deal_sock, control_sock, session_id)
    
    if control_msg is None or control_msg.payload == "kill server":
        # terminate all sockets
        pub_sock.send_string("kill")
        while threading.activeCount() > 1:
            time.sleep(0.1) # wait until all handler threads have terminated    

        rout_sock.close()
        deal_sock.close()
        pub_sock.close()
        logging.info('terminating server')
        return True
    else:
        return False
