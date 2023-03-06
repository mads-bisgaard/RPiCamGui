#!/bin/python

import zmq
import threading
import logging
from .handler import request_handler
from RPiCamInterface import Message, MessageType
import time
from typing import Optional, List




def proxy(frontend: zmq.Socket, backend: zmq.Socket) -> Optional[Message]:
    """
    Simple control proxy. Before forwarding messages it checks that they have the correct session id.
    One can also control (exit) the proxy by sending suitable messages
    """
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)

    session_id: Optional[str] = None
    
    def update_frontend(response: Message, frontend: zmq.Socket, msg_id: bytes, blank: bytes, s: str):
        logging.info(s)
        response.payload = s
        frontend.send_multipart([msg_id, blank, response.to_bytes()])
        

    while True:
        try:
            socks = dict(poller.poll())
        except KeyboardInterrupt:
            return None
        if frontend in socks:
            msg_id, blank, msg_b = frontend.recv_multipart()
            msg = Message.from_bytes(msg_b)
            response = Message()
            response.type = msg.type
            response.session_id = msg.session_id
            s: Optional[str]= None
            if session_id is None:
                if (msg.type == MessageType.BEGIN_SESSION):
                    session_id = msg.session_id
                    s = f"initiating session {session_id}"
                    update_frontend(response, frontend, msg_id, blank, s)
                else:
                    s = f"Session must be initiated before a message of type {str(msg.type)} is accepted"
                    update_frontend(response, frontend, msg_id, blank, s)
            elif msg.session_id == session_id:
                if (msg.type == MessageType.END_SESSION):
                    s = f"ending session {session_id}"
                    update_frontend(response, frontend, msg_id, blank, s)
                    session_id = None
                elif (msg.type == MessageType.KILL_SERVER):
                    s = f"Succesfully killed server from session {session_id}"
                    update_frontend(response, frontend, msg_id, blank, s)
                    return
                else:
                    s = "Received invalid message type"
                    update_frontend(response, frontend, msg_id, blank, s)
            else:
                s = "Received invalid session id. Server cannot accept command"
                update_frontend(response, frontend, msg_id, blank, s)
        if backend in socks:
            frontend.send_multipart(backend.recv_multipart())
                

def run_session(rout_port: int, n_threads: int = 1) -> None:
    """
    Server which should be running on Rpi
    """
    assert n_threads > 0, 'server requires at least one thread running a worker'
    context: zmq.Context = zmq.Context()
    
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
    
    handlers: List[threading.Thread] = []
    for _ in range(n_threads):
        thread = threading.Thread(target=request_handler, args=(context, deal_addr, pub_addr))
        thread.daemon = True
        thread.start()
        handlers.append(thread)
    
    proxy(rout_sock, deal_sock)
    
    # terminate all sockets
    pub_sock.send_string("kill")
    for h in handlers:
        h.join()

    rout_sock.close()
    deal_sock.close()
    pub_sock.close()
    logging.info('terminating server')
    