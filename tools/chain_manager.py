import logging as log
import requests
from web3 import Web3
from includes.config import INFURA_KEY


class ChainManager:
    chains_url = "https://chainid.network/chains.json"

    def __init__(self, chains_to_check) -> None:
        self.chains_to_check = chains_to_check
        self.chains = self.get_chains()

    def get_chains(self):
        res = requests.get(self.chains_url)
        return self.parse_chains(res.json()) if res.status_code == 200 else {}

    def parse_chains(self, chains: list) -> dict:
        parsed_chains = {}
        for chain in chains:
            chainId = chain["chainId"]
            if chainId in self.chains_to_check:
                decimals = chain["nativeCurrency"]["decimals"]
                symbol = chain["nativeCurrency"]["symbol"]
                if decimals != 18:
                    log.warning(
                        f"Decimals for {symbol} is {decimals} - ONLY 18 is supported"
                    )
                else:
                    parsed_chains[chainId] = chain
        return parsed_chains

    def new_rpc(self, chainId: int) -> Web3:
        rpc = self.chains[chainId]["rpc"][0]
        rpc = (
            rpc.replace("${INFURA_API_KEY}", INFURA_KEY)
            if rpc.endswith("${INFURA_API_KEY}")
            else rpc
        )
        log.info(
            f"RPC Changed to: {rpc} | Chain: {self.chains[chainId]['nativeCurrency']['symbol']} | ChainId: {chainId}"
        )
        return Web3(Web3.HTTPProvider(rpc))
