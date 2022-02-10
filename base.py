from web3 import Web3, exceptions
from ethtoken.abi import EIP20_ABI
from web3_base.includes.config import *
import logging as log

class OneTransfer:
    def __init__(self, w3, key, chain_id=1666600000, abi=EIP20_ABI) -> None:
        self.w3 = w3
        self.key = key
        self.chain_id = chain_id
        w3.eth.default_account = w3.eth.account.privateKeyToAccount(key).address
        self.account = w3.eth.default_account
        self.abi = abi

    def is_connected(self):
        return self.w3.isConnected()

    def balance(self, address):
        return self.w3.fromWei(self.w3.eth.getBalance(address), "ether")

    def check_details(self):
        log.info(self.is_connected())
        log.info(self.account)
        log.info(self.balance(self.account))

    def sign_transaction(self, data: dict):
        return self.w3.eth.account.sign_transaction(
            data,
            self.key,
        )

    def build_transaction(
        self,
        nonce: int,
        gasPrice: int,
        address_to: str,
        value: int,
        manual_nonce: bool = False,
        contract=False,
    ) -> list:

        if not manual_nonce:
            nonce = self.w3.eth.get_transaction_count(self.account)
        log.info(f"gas  ::  {gasPrice} |  Nonce  ::  {nonce}  | Value :: {value}")

        tx_data = dict(
            chainId=self.chain_id,
            nonce=nonce,
            gasPrice=gasPrice,
            to=address_to,
            value=value,
        )

        if contract:
            tx_data = self.build_hrc20_transfer(
                contract, address_to, value, nonce, gasPrice
            )

        signed_txn = self.sign_transaction(tx_data)

        return signed_txn, value, nonce

    def build_hrc20_transfer(
        self,
        contract: str,
        send_address: str,
        send_amount: int,
        nonce: int,
        gas_price: int,
    ):
        contract = self.w3.eth.contract(address=contract, abi=self.abi)
        txn = contract.functions.transferFrom(self.account, send_address, send_amount).buildTransaction(
            {
                "gasPrice": gas_price,
                "nonce": nonce,
                "chainId": self.chain_id,
            }
        )
        return txn

    def tx_function(self, func: object, gas_price: int, func_args: tuple=(), value: int = 0) -> str:

        # Convert to Wei and get nonce
        nonce = self.w3.eth.getTransactionCount(self.account)

        # Build transaction using the function and arguments prior
        tx = func(*func_args).buildTransaction(
            {
                "from": self.account,
                "nonce": nonce,
                "chainId": self.chain_id,
                "gasPrice": gas_price,
                "value": value,
            }
        )
        signed_tx = self.w3.eth.account.signTransaction(tx, self.key)
        return signed_tx, value, nonce

    def process_tx(self, signed_txn: list) -> list:
        signed_txn, value, nonce = signed_txn

        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            log.info("Waiting for Tx... ")
            sent, hash_info = self.wait_for_receipt(tx_hash)
            found = dict(hash_info)
            info = f"\n\nCheck Completed Tx for :: {tx_hash.hex()}\n\n"
            self.check_tx_hash(found, info)
            log.info(f"SUCCESS! {tx_hash.hex()}  :: {value}  ::  {nonce}")
            return True, nonce
        except ValueError as e:
            log.error(e)
        return False, nonce, None

    def check_tx_hash(self, found: dict, info: str) -> None:
        log.info(info)
        for k, v in found.items():
            try:
                log.info(f"{k} : {v.hex()}")
            except AttributeError:
                log.info(f"{k} : {v}")

    def wait_for_receipt(self, t_hash: str) -> tuple:
        while 1:
            try:
                hash_info = self.w3.eth.getTransaction(t_hash)
                sent = self.w3.eth.getTransactionReceipt(t_hash)
                log.info(sent)
                return sent, hash_info
            except exceptions.TransactionNotFound:
                pass


# if __name__ == "__main__":

#     contract = "0x6058c4ac419fa0D76c9dDc65ec765da8E9238518"
#     fn = os.path.join("abis", "steak.json")

#     p_keyCreator = ""
#     abi = get_abi(fn)
#     w3 = Web3(Web3.WebsocketProvider(wss_url))
#     tx = OneTransfer(w3, p_keyCreator, abi=abi)
#     tx.check_details()

#     steakwallet1 = "0x1Ef8CA159D1e3bA31Ff9f557B08D977fB60F2ac1"
#     value = tx.w3.toWei(200000000, "ether")
#     gas_price = tx.w3.eth.gas_price
#     print(gas_price)
#     signed_txn = tx.build_transaction(
#         0, gas_price, steakwallet1, value, contract=contract
#     )
#     tx.process_tx(signed_txn)
