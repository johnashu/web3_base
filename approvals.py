import os
import logging as log
from tools.utils import get_abi
from web3_base import Web3Base, INFURA_KEY, Web3, envs
from tools.chain_manager import ChainManager


class Approvals(Web3Base):
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

    def set_approval_for_all(
        self, operator_address: str, approved: bool, token_contract: str, **kw
    ) -> str:

        # Get the gas price
        gas_price = self.w3.eth.gas_price

        # Build the transaction
        contract = self.w3.eth.contract(address=token_contract, abi=self.abi)

        tx = self.build_tx_with_function(
            contract.functions.setApprovalForAll,
            gas_price,
            (operator_address, approved),
        )
        # Send the transaction
        self.process_tx(tx)


if __name__ == "__main__":
    chains = {1: "ETH", 137: "MATIC", 1285: "MOVR", 22776: "MAPO", 5: "Goerli ETH"}
    fn = os.path.join("abis", "ERC721.json")
    abi = get_abi(fn)

    print("\n\nabi", abi)
    chainId = 5
    token_contract = "0x0243C9b7F547E5D74a38039958FB347354F5746d"
    operator_address = "0x00000000000000ADc04C56Bf30aC9d3c0aAF14dC"  # Seaport
    chain_manager = ChainManager(chains)
    sender = Approvals(chain_manager, False, envs.PK, abi=abi)
    sender.update_chain(chainId)

    sender.set_approval_for_all(operator_address, False, token_contract)
