import logging as log
from web3_base import Web3Base, INFURA_KEY, Web3, envs
from tools.chain_manager import ChainManager


class SendERC20(Web3Base):
    def __init__(self, chain_manager, *args, **kw) -> None:
        super().__init__(
            *args,
            **kw,
        )
        self.chain_manager = chain_manager
        self.chains = chain_manager.chains

    def update_chain(self, chainId: int) -> None:
        self.w3 = self.chain_manager.new_rpc(chainId)
        self.set_web3(self.w3, self.key, chainId)
        self.check_details()

    def send_erc20(
        self, to_address: str, amount: float, token_contract: str, **kw
    ) -> str:

        # Convert the amount to Wei
        amount_in_wei = self.w3.toWei(amount, "ether")

        # Get the gas price
        gas_price = self.w3.eth.gas_price

        # Build the transaction
        tx = self.build_transaction(
            0, gas_price, to_address, amount_in_wei, contract=token_contract, **kw
        )

        # Send the transaction
        self.process_tx(tx)


if __name__ == "__main__":
    chains = {1: "ETH", 137: "MATIC", 1285: "MOVR", 22776: "MAPO"}
    chainId = 137
    send_to = "0x81cF5e49c973BcB3CD013D4D9C99890E0ae86332"
    amount = 0.001
    token_contract = "0x5c4b7CCBF908E64F32e12c6650ec0C96d717f03F"  # BNB MATIC

    chain_manager = ChainManager(chains)
    sender = SendERC20(chain_manager, False, envs.PK)
    sender.update_chain(chainId)

    sender.send_erc20(send_to, amount, token_contract)
