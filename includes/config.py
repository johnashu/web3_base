from includes._logger import *
from includes.config_utils import Envs, create_data_path

envs = Envs()
INFURA_KEY = envs.INFURA_KEY

test_net = "https://api.s0.b.hmny.io/"
wss_url = "wss://ws.s0.t.hmny.io"
# main_net = "https://api.harmony.one"
main_net = f"https://mainnet.infura.io/v3/{INFURA_KEY}"

create_data_path("", data_path="logs")
create_data_path("", data_path="data")

##############################################

log = start_logger()

places = 1000000000000000000
chain_id = 1
# chain_id = 1666700000
gas_price = 300000000000
gas = 25000
