import logging as log
import requests, json
from typing import Tuple
from datetime import datetime as dt, timedelta as td
from time import time
from web3 import Web3, exceptions
from ethtoken.abi import EIP20_ABI


class Web3Base:
    def __init__(
        self,
        w3: Web3,
        key: str,
        chain_id: int = 1666600000,
        abi: list = EIP20_ABI,
        abi_from_api: bool = False,
    ) -> None:
        self.w3 = w3
        self.key = key
        self.chain_id = chain_id
        w3.eth.default_account = w3.eth.account.privateKeyToAccount(key).address
        self.account = w3.eth.default_account
        self.abi = abi

    def is_connected(self) -> bool:
        return self.w3.isConnected()

    def balance(self, address: str = "") -> float:
        if not address:
            address = self.account
        return self.w3.fromWei(self.w3.eth.getBalance(address), "ether")

    def check_details(self) -> None:
        log.info(f"Connected?   ::  {self.is_connected()}")
        log.info(f"Address      ::  {self.account}")
        log.info(f"Balance      ::  {self.balance(self.account)}")

    def get_abi_from_api(
        self, contract: str, add_to_object: bool = False
    ) -> Tuple[bool, list]:
        """Harmony ONE"""

        api = "https://ctrver.t.hmny.io/fetchContractCode"
        params = {"contractAddress": contract}

        res = requests.get(api, params=params)
        if res.status_code == 200:
            abi = res.json()["abi"]
            if add_to_object:
                self.abi = abi
            return True, abi
        return False, [{"Error": res.text}]

    def save_abi_from_api(self, fn: str, contract: str) -> None:
        res, abi = self.get_abi_from_api(contract)
        if res:
            with open(fn, "w") as j:
                json.dump(abi, j, ensure_ascii=False, indent=4)
        else:
            log.error(f"Cannot find contract ABI  ::  {abi}")

    def sign_transaction(self, data: dict) -> Web3:
        return self.w3.eth.account.sign_transaction(
            data,
            self.key,
        )

    def get_nonce(self) -> int:
        return self.w3.eth.getTransactionCount(self.account)

    def build_transaction(
        self,
        nonce: int,
        gasPrice: int,
        address_to: str,
        value: int,
        manual_nonce: bool = False,
        contract=False,
    ) -> tuple:

        if not manual_nonce:
            nonce = self.get_nonce()
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
    ) -> Web3:
        contract = self.w3.eth.contract(address=contract, abi=self.abi)
        txn = contract.functions.transferFrom(
            self.account, send_address, send_amount
        ).buildTransaction(
            {
                "gasPrice": gas_price,
                "nonce": nonce,
                "chainId": self.chain_id,
            }
        )
        return txn

    def build_tx_with_function(
        self,
        func: object,
        gas_price: int,
        func_args: tuple = (),
        value: int = 0,
        nonce: int = 0,
        manual_nonce=False,
    ) -> tuple:

        gas = 30000000

        # Convert to Wei and get nonce
        if not manual_nonce:
            nonce = self.get_nonce()

        # Build transaction using the function and arguments prior
        tx = func(*func_args).buildTransaction(
            {
                "from": self.account,
                "nonce": nonce,
                "chainId": self.chain_id,
                "gasPrice": gas_price,
                "gas": gas,
                "value": value,
            }
        )
        signed_tx = self.sign_transaction(tx)
        return signed_tx, value, nonce

    def process_tx(
        self,
        signed_txn: list,
        display_tx_hash: bool = False,
        display_receipt: bool = False,
        manual_raw: bool = False,
        show_logs: bool = True,
        no_check: bool = False,
    ) -> list:
        signed_txn, value, nonce = signed_txn

        raw = signed_txn
        if not manual_raw:
            raw = signed_txn.rawTransaction

        try:
            tx_hash = self.w3.eth.send_raw_transaction(raw)
            if no_check:
                return True, nonce
            if show_logs:
                log.info("Waiting for Tx... ")
            receipt, hash_info = self.wait_for_receipt(tx_hash)
            info = f"\n\nCheck Completed Tx for :: {tx_hash.hex()}\n\n"
            if display_tx_hash:
                self.check_tx_hash(hash_info, info)
            if display_receipt:
                self.check_tx_hash(receipt, info)
            if show_logs:
                log.info(f"SUCCESS! {tx_hash.hex()}  :: {value}  ::  {nonce}")
            return True, nonce
        except ValueError as e:
            log.error(e)
        return False, nonce

    def check_tx_hash(self, found: dict, info: str) -> None:
        log.info(info)
        display = ""
        for k, v in found.items():
            try:
                display += f"\t{k} : {v.hex()}\n"
            except AttributeError:
                display += f"\t{k} : {v}\n"
        log.info(f"\n{display}")

    def wait_for_receipt(self, t_hash: str, timeout: int = 600) -> tuple:
        to = dt.now() + td(seconds=timeout)
        while 1:
            now = dt.now()
            if now > to:
                err = f"Waiting for receipt timed out after [ {timeout} ] seconds..."
                log.error(err)
                break
            try:
                hash_info = self.w3.eth.getTransaction(t_hash)
                receipt = self.w3.eth.getTransactionReceipt(t_hash)
                log.debug(receipt)
                return dict(receipt), dict(hash_info)
            except exceptions.TransactionNotFound:
                pass

        return {"error": err}, {"error": err}


# if __name__ == "__main__":

#     contract = ""
#     fn = os.path.join("abis", "ERC20.json")

#     p_keyCreator = ""
#     abi = get_abi(fn)
#     w3 = Web3(Web3.WebsocketProvider(wss_url))
#     tx = Web3Base(w3, p_keyCreator, abi=abi)
#     tx.check_details()

#     wallet = ""
#     value = tx.w3.toWei(200000000, "ether")
#     gas_price = tx.w3.eth.gas_price
#     print(gas_price)
#     signed_txn = tx.build_transaction(
#         0, gas_price, wallet, value, contract=contract
#     )
#     tx.process_tx(signed_txn)
