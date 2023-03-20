#!/bin/python

import zmq
import threading
import logging
from .handler import request_handler
from RPiCamInterface import Message, MessageType, ExitCode, RequestPayload, ReceivePayload
from typing import Optional, List
from uuid import uuid4, UUID


def proxy(frontend: zmq.Socket, backend: zmq.Socket) -> None:
    """
    Proxy
    Messages are only forwarded frontends -> backend if they have the correct session id.
    Messages backend -> frontend are always forwarded
    Proxy can be killed from frontend
    """
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)

    def update_frontend(frontend: zmq.Socket, msg_id: bytes, msg_type: MessageType, session_id: Optional[UUID], blank: bytes, exitcode: ExitCode, msg: str):
        logging.info(f'Sending message to frontend: {msg}')
        response = Message()
        response.payload = ReceivePayload(dict({'exitcode': int(exitcode), 'msg': msg}))
        response.type = msg_type
        response.session_id = None if session_id is None else session_id
        frontend.send_multipart([msg_id, blank, response.to_bytes()])
        
    session_id: Optional[UUID] = None
    while True:
        try:
            socks = dict(poller.poll())
        except KeyboardInterrupt:
            return None
        
        if backend in socks:
            frontend.send_multipart(backend.recv_multipart())

        if frontend in socks:
            msg_id, blank, msg_b = frontend.recv_multipart()
            msg = Message.from_bytes(msg_b)
            if session_id is None:
                if (msg.type == MessageType.BEGIN_SESSION):
                    session_id = uuid4()
                    update_frontend(frontend, msg_id, msg.type, session_id, blank, ExitCode.Success, f'Succesfully connected to session {session_id}')
                else:
                    update_frontend(frontend, msg_id, msg.type, session_id, blank, ExitCode.Failure, f'A session must be initiated before other commands can be received')
                continue
            if session_id != msg.session_id:
                update_frontend(frontend, msg_id, msg.type, session_id, blank, ExitCode.Failure, f'Received invalid session_id {msg.session_id}')
                continue
            # session_id is valid and session is running
            if (msg.type == MessageType.END_SESSION):
                update_frontend(frontend, msg_id, msg.type, session_id, blank, ExitCode.Success, f'Terminating session {msg.session_id}')
                session_id = None
            elif (msg.type == MessageType.KILL_SERVER):
                update_frontend(frontend, msg_id, msg.type, session_id, blank, ExitCode.Success, f'Terminating server')
                return
            elif (msg.type == MessageType.COMMAND):
                backend.send_multipart([msg_id, blank, msg_b])
            else:
                update_frontend(frontend, msg_id, msg.type, session_id, blank, ExitCode.Failure, f'Received invalid message type')
        
                

def run_server(rout_port: int, n_threads: int = 1) -> None:
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
    
    try:
        proxy(rout_sock, deal_sock)
    except Exception as e:
        logging.error(f'Encountered exception {e}')        
    finally:
        # terminate all sockets
        pub_sock.send_string("kill")
        for h in handlers:
            h.join()

        rout_sock.close()
        deal_sock.close()
        pub_sock.close()
        logging.info('terminating server')
    