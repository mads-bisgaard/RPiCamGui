#!/bin/python

import zmq
import threading
import logging
from .handler import request_handler
from RPiCamInterface import Message, MessageType
import time



def proxy(frontend: zmq.Socket, backend: zmq.Socket, control: zmq.Socket):
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
            return
        if frontend in socks:
            backend.send_multipart(frontend.recv_multipart())
        if backend in socks:
            frontend.send_multipart(backend.recv_multipart())
        if control in socks:
            return
                

def run_server(rout_port: int, control_port: int, n_threads: int = 1) -> None:
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
    
    # socket for controling server 
    control_sock: zmq.Socket = context.socket(zmq.REP) 
    control_addr: str = f"tcp://*:{control_port}"
    logging.info(f"binding control socket to {control_addr}")
    control_sock.bind(control_addr)

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
        thread = threading.Thread(target=request_handler, args=(context, deal_addr, pub_addr))
        thread.daemon = True
        thread.start()
    
    proxy(rout_sock, deal_sock, control_sock)
    
    # terminate all sockets
    pub_sock.send(b'')
    while threading.activeCount() > 1:
        time.sleep(0.1) # wait until all handler threads have terminated
    control_sock.send(b'') # tell client server has terminated

    rout_sock.close()
    deal_sock.close()
    pub_sock.close()
    control_sock.close()
    context.destroy()
    logging.info('terminating server')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_server(1234, 1235)