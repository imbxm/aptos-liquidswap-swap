import sys
import random
from loguru import logger
from liquidswap.client import LiquidSwapClient
from config import node_url, tokens_mapping, show_balance_before_swap, show_balance_after_swap

if __name__ == "__main__":
    with open('wallets.txt', 'r', encoding='utf-8-sig') as file:
        wallets = [line.strip() for line in file]

    for wallet in wallets:
        liquidswap_client = LiquidSwapClient(node_url, tokens_mapping, wallet)
        liquidswap_client.client_config.max_gas_amount = 5_000
        from_token = str(sys.argv[1])
        to_token = str(sys.argv[2])
        from_amount = float(sys.argv[3])
        to_amount = float(sys.argv[4])

        amount = round(random.uniform(from_amount, to_amount), 2)

        try:
            if show_balance_before_swap:
                logger.info(f"Баланс {from_token}: {liquidswap_client.get_token_balance(from_token)}; "
                            f"Баланс {to_token}: {liquidswap_client.get_token_balance(to_token)}")

            coins_in = liquidswap_client.calculate_rates(from_token, to_token, amount)
            coins_out = liquidswap_client.calculate_rates(to_token, from_token, coins_in)

            logger.warning(f"Попытка свапнуть {coins_out} {from_token} в {coins_in} {to_token}")
            liquidswap_client.swap(from_token, to_token, amount, coins_in)

            if show_balance_after_swap:
                logger.info(f"Баланс {from_token}: {liquidswap_client.get_token_balance(from_token)}; "
                            f"Баланс {to_token}: {liquidswap_client.get_token_balance(to_token)}")
        except Exception:
            logger.error(f"Непредвиденная ошибка")
