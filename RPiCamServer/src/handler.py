
import logging
import zmq
import msgpack
import threading
from RPiCamInterface import Message, MessageType, ReceivePayload, ExitCode

def request_handler(context: zmq.Context, work_url: str, control_url: str):
    """
    Fcn which handles requests coming from the server entrypoint
    Args:
        url (str): address to which socket should connect
        port (int): port number to which socket should connect
    """
    work_sock = context.socket(zmq.DEALER)
    logging.info(f"connecting request handler work socket on thread {threading.current_thread().ident}")
    work_sock.connect(work_url)
    
    control_sock: zmq.Socket = context.socket(zmq.SUB)
    control_sock.connect(control_url)
    control_sock.subscribe("")
    
    poller = zmq.Poller()
    poller.register(work_sock, zmq.POLLIN)
    poller.register(control_sock, zmq.POLLIN)
    
    while True:
        
        try:
            socks = dict(poller.poll())
        except KeyboardInterrupt:
            break

        if control_sock in socks:
            msg = control_sock.recv_string()
            assert msg == "kill", f'Received invalid termination command in handler on thread {threading.current_thread().ident}'
            logging.info(f'terminating thread {threading.current_thread().ident}')
            work_sock.close()
            control_sock.close()
            return                
        if work_sock in socks:
            msg_id, blank, msg_b = work_sock.recv_multipart()
            msg = Message.from_bytes(msg_b)
            # handle requests here
            msg.payload = ReceivePayload()
            msg.payload.exitcode = ExitCode.Success
            work_sock.send_multipart([msg_id, blank, msg.to_bytes()])
