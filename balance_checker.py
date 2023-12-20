import logging as log
from web3_base import Web3Base, INFURA_KEY, Web3, envs
from tools.chain_manager import ChainManager


class BalanceChecker(Web3Base):
    def __init__(self, chain_manager, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self.balances = {}
        self.chain_manager = chain_manager
        self.chains = chain_manager.chains

    def get_balance_of_chain(self, address: str, chainId: int) -> float:
        self.w3 = self.chain_manager.new_rpc(chainId)
        return self.balance(address)

    def get_all_balances(self, address: str) -> dict:
        self.balances = {
            self.chains[chainId]["nativeCurrency"]["symbol"]: self.get_balance_of_chain(
                address, chainId
            )
            for chainId in self.chains
        }
        return self.balances

    def display_balances(self, address: str) -> None:
        self.get_all_balances(address)
        for symbol, balance in self.balances.items():
            log.info(f"{symbol:<6} :: {balance}")


if __name__ == "__main__":
    chains_to_check = {1: "ETH", 137: "MATIC", 1285: "MOVR", 22776: "MAPO"}

    chain_manager = ChainManager(chains_to_check)
    checker = BalanceChecker(chain_manager, False, envs.PK)
    checker.display_balances(envs.WALLET)
