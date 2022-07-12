from web3_base.includes._logger import *
from web3_base.includes.config_utils import Envs, create_data_path

test_net = "https://api.s0.b.hmny.io/"
wss_url = "wss://ws.s0.t.hmny.io"
# main_net = "https://api.harmony.one"
main_net = "https://harmony-0-rpc.gateway.pokt.network"

envs = Envs()
create_data_path("", data_path="logs")
create_data_path("", data_path="data")

##############################################

log = start_logger()

places = 1000000000000000000
chain_id = 1666600000
# chain_id = 1666700000
gas_price = 300000000000
gas = 25000
