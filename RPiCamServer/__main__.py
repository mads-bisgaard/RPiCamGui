from argparse import ArgumentParser
import logging
from .src.server import run_server

parser = ArgumentParser()
parser.add_argument('server_port', type=int, help='port on which the socket should bind')
parser.add_argument('-n_threads', type=int, default='1', help='number of threads on which server should be running')
parser.add_argument('-log_level', type=str, default='error', help='info, error or fatal')

args = parser.parse_args()
ll = args.log_level.upper()
assert (ll in dir(logging)) and isinstance(getattr(logging, ll), int)
logging.basicConfig(level=getattr(logging, ll))

run_server(args.server_port, args.n_threads)
