
import logging
import zmq
import msgpack

def request_handler(context: zmq.Context, url: str):
    """
    Fcn which handles requests coming from the server entrypoint
    Args:
        url (str): address to which socket should connect
        port (int): port number to which socket should connect
    """
    sock = context.socket(zmq.REP)
    logging.info(f"connecting socket to {url}")
    sock.connect(url)
    
    while True:
        msg = msgpack.unpackb(sock.recv())
        logging.info(f"received request: {msg}")
        sock.send(msgpack.packb("world"))
    
    