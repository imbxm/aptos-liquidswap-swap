import sys
from loguru import logger
from liquidswap.client import LiquidSwapClient
from config import node_url, tokens_mapping, wallet_path, show_balance_before_swap, show_balance_after_swap

if __name__ == "__main__":
    liquidswap_client = LiquidSwapClient(node_url, tokens_mapping, wallet_path)
    from_token = str(sys.argv[1])
    to_token = str(sys.argv[2])
    amount = float(sys.argv[3])

    try:
        if show_balance_before_swap:
            logger.info(f"Баланс {from_token}: {liquidswap_client.get_token_balance(from_token)}")
            logger.info(f"Баланс {to_token}: {liquidswap_client.get_token_balance(to_token)}")

        coins_in = liquidswap_client.calculate_rates(from_token, to_token, amount)
        coins_out = liquidswap_client.calculate_rates(to_token, from_token, coins_in)

        logger.warning(f"Попытка свапнуть {coins_out} {from_token} в {coins_in} {to_token}")
        liquidswap_client.swap(from_token, to_token, amount, coins_in)

        if show_balance_after_swap:
            logger.info(f"Баланс {from_token}: {liquidswap_client.get_token_balance(from_token)}")
            logger.info(f"Баланс {to_token}: {liquidswap_client.get_token_balance(to_token)}")
    except Exception:
        logger.error(f"Непредвиденная ошибка")
