import logging as log
from web3_base import *

class BalanceChecker(Web3Base):
    chains_url = "https://chainid.network/chains.json"

    def __init__(self, chains_to_check, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self.balances = {}
        self.chains_to_check = chains_to_check
        self.chains = self.get_chains()

    def get_chains(self):
        res = requests.get(self.chains_url)
        return self.parse_chains(res.json()) if res.status_code == 200 else {}

    def parse_chains(self, chains: list) -> list:
        return {chain["chainId"]: chain for chain in chains if chain["chainId"] in self.chains_to_check}

    
    def get_balance_of_chain(self, address: str, chainId: int) -> float:
        rpc = self.chains[chainId]["rpc"][0]
        rpc = rpc.replace("${INFURA_API_KEY}", INFURA_KEY) if rpc.endswith("${INFURA_API_KEY}") else rpc
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        decimals = self.chains[chainId]["nativeCurrency"]["decimals"]
        symbol = self.chains[chainId]["nativeCurrency"]["symbol"]
        if decimals != 18:
            log.warning(f"Decimals for {symbol} is {decimals} - ONLY 18 is supported")
            return -0
        return self.balance(address)
    
    def get_all_balances(self, address: str) -> dict:
        self.balances = {self.chains[chainId]["nativeCurrency"]["symbol"]: self.get_balance_of_chain(address, chainId) for chainId in self.chains}
        return self.balances
    
    def display_balances(self, address: str) -> None:
        self.get_all_balances(address)
        for symbol, balance in self.balances.items():
            log.info(f"{symbol:<6} :: {balance}")
                

if __name__ == "__main__":

    chains_to_check = {
        1: "ETH", 
        137: "MATIC",
        1285: "MOVR",
        22776: "MAPO"
    }

    checker = BalanceChecker(chains_to_check, False, envs.PK)
    checker.display_balances(envs.WALLET)
    
