from typing import Union
from loguru import logger
from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.bcs import Serializer
from aptos_sdk.client import RestClient
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.type_tag import StructTag, TypeTag

from .constants import (
    COIN_INFO,
    NETWORKS_MODULES,
    RESOURCES_ACCOUNT,
    FEE_SCALE,
    FEE_PCT,
    CURVES,
)


class LiquidSwapClient(RestClient):
    def __init__(self, node_url: str, tokens_mapping: dict, account: str):
        super().__init__(node_url)
        self.tokens_mapping = tokens_mapping
        self.my_account = Account.load(account)

    def get_coin_info(self, token: str) -> int:
        token = self.tokens_mapping[token]
        data = self.account_resource(
            AccountAddress.from_hex(token.split("::")[0]),
            f"{COIN_INFO}<{token}>",
        )["data"]
        return data["decimals"]

    def convert_to_decimals(self, amount: float, token: str) -> int:
        d = self.get_coin_info(token)
        return int(amount * 10 ** d)

    def pretty_amount(self, amount: int, token: str) -> float:
        d = self.get_coin_info(token)
        return float(amount / 10 ** d)

    def get_token_reserves(self, token_x: str, token_y: str) -> (float, float):
        resource_type = f"{NETWORKS_MODULES['LiquidityPool']}::LiquidityPool<{self.tokens_mapping[token_x]}," \
                        f" {self.tokens_mapping[token_y]}, {CURVES}>"
        data = self.account_resource(
            AccountAddress.from_hex(RESOURCES_ACCOUNT),
            resource_type,
        )["data"]
        coin_x_reserve_value = int(data["coin_x_reserve"]["value"])
        coin_y_reserve_value = int(data["coin_y_reserve"]["value"])
        from_token_reserve = self.pretty_amount(coin_x_reserve_value, token_x)
        to_token_reserve = self.pretty_amount(coin_y_reserve_value, token_y)
        return from_token_reserve, to_token_reserve

    def calculate_rates(self, from_token: str, to_token: str, amount: float) -> float:
        try:
            from_token_reserve, to_token_reserve = self.get_token_reserves(from_token, to_token)
        except Exception:
            to_token_reserve, from_token_reserve = self.get_token_reserves(to_token, from_token)

        coin_in_after_fees = amount * (FEE_SCALE - FEE_PCT)
        new_reserves_in_size = from_token_reserve * FEE_SCALE + coin_in_after_fees

        return float(coin_in_after_fees * to_token_reserve / new_reserves_in_size)

    def get_token_balance(self, token: str) -> float:
        coin_data = self.get_coin_data(token)
        return self.pretty_amount(int(coin_data), token) if coin_data is not None else 0

    def get_coin_data(self, token: str) -> Union[dict, None]:
        try:
            coin_data = self.account_resource(
                self.my_account.address(),
                f"0x1::coin::CoinStore<{self.tokens_mapping.get(token)}>") \
                .get("data", {}) \
                .get("coin", {}) \
                .get("value")
            return coin_data
        except Exception:
            return None

    def register(self, token: str) -> None:
        payload = EntryFunction.natural(
            "0x1::managed_coin",
            "register",
            [
                TypeTag(StructTag.from_str(self.tokens_mapping[token])),
            ],
            [],
        )
        signed_transaction = self.create_bcs_signed_transaction(
            self.my_account, TransactionPayload(payload)
        )
        tx = self.submit_bcs_transaction(signed_transaction)
        self.wait_for_transaction(tx)
        logger.success(
            f"Успешно зарегистрированная монета: {token}.\nHash: https://explorer.aptoslabs.com/txn/{tx}?network=mainnet")

    def swap(self, from_token: str, to_token: str, from_amount: float, to_amount: float) -> None:

        if self.get_coin_data(to_token) is None:
            self.register(to_token)

        payload = EntryFunction.natural(
            NETWORKS_MODULES["Scripts"],
            "swap",
            [
                TypeTag(StructTag.from_str(self.tokens_mapping[from_token])),
                TypeTag(StructTag.from_str(self.tokens_mapping[to_token])),
                TypeTag(StructTag.from_str(CURVES)),
            ],
            [
                TransactionArgument(
                    self.convert_to_decimals(from_amount, from_token),
                    Serializer.u64,
                ),
                TransactionArgument(
                    self.convert_to_decimals(to_amount, to_token),
                    Serializer.u64,
                ),
            ],
        )
        signed_transaction = self.create_bcs_signed_transaction(
            self.my_account, TransactionPayload(payload)
        )
        tx = self.submit_bcs_transaction(signed_transaction)
        self.wait_for_transaction(tx)
        logger.success(f"Транзакция успешно выполнена.\nHash: https://explorer.aptoslabs.com/txn/{tx}?network=mainnet")
