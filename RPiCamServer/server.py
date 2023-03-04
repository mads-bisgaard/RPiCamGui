#!/bin/python

import zmq
import threading
import logging
from handler import request_handler


def run_server(rep_url: str, rep_port: int, nthreads: int = 1) -> None:
    """
    Server which should be running on Rpi
    """

    context: zmq.Context = zmq.Context()
    
    # socket for receiving incomming requests
    rep_sock: zmq.Socket = context.socket(zmq.ROUTER) # TODO: need to change this to a rep socket
    rep_addr: str = f"tcp://{rep_url}:{rep_port}"
    logging.info(f"binding rep socket to {rep_addr}")
    rep_sock.bind(rep_addr)
    
    # socket for dealing requests to thread handling camera
    deal_sock = context.socket(zmq.DEALER)
    deal_addr: str = f"inproc://handlers"
    logging.info(f"binding deal socket to {deal_addr}")
    deal_sock.bind(deal_addr)
    
    for ii in range(nthreads):
        thread = threading.Thread(target=request_handler, args=(context, deal_addr))
        thread.daemon = True
        thread.start()
    
    zmq.proxy(rep_sock, deal_sock)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_server("*", 1234)