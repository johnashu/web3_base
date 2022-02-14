from web3 import Web3
import sys, os
import json


def check_connections(w3: Web3) -> bool:
    is_connected = w3.isConnected()

    if not is_connected:
        print("Not Connected")
        sys.exit()
    print(f"Connected :: {is_connected}")


def get_abi(fn: str) -> json:
    with open(fn) as j:
        return list(json.load(j))


def readable_price(num, d: int = 18, show_decimals=True, print_res=True):
    temp = []
    c = 1
    try:
        main, decimals = f"{num / 10 ** d:.{d}f}".split(".")
    except ValueError:
        return float(num)

    for d in reversed(main):
        temp.insert(0, d)
        if c == 3:
            temp.insert(0, ",")
            c = 1
        else:
            c += 1

    if not show_decimals:
        decimals = ""

    rtn_str = "".join(temp)
    rtn_str += f".{decimals}" if show_decimals else ""
    if rtn_str[0] == ",":
        rtn_str = rtn_str[1:]

    if print_res:
        print(rtn_str)
    return rtn_str
