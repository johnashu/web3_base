import logging
import sys, os
import json

from web3_base.includes.config_utils import Envs, create_data_path

test_net = "https://api.s0.b.hmny.io/"
wss_url = "wss://ws.s0.t.hmny.io"
main_net = "https://api.harmony.one"

envs = Envs()
print(envs)

##############################################


# LOGGING

file_handler = logging.FileHandler(filename="data.log")
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] <%(funcName)s> %(message)s",
    handlers=handlers,
    datefmt="%d-%m-%Y %H:%M:%S",
)

log = logging.getLogger()

places = 1000000000000000000
chain_id = 1666600000
# chain_id = 1666700000
gas_price = 300000000000
gas = 25000
