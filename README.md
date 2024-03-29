# aptos-liquidswap-swap

Скрипт для свапов в сети Aptos с использованием DEX Liquidswap

#### Установка зависимостей: ```pip install -r requirements.txt```

- `wallet.txt` для ввода приватников
- `config.py`  дефолтные настройки, также можно настроить время ожидания между кошельками, включить рандомизацию кошельков
- `tokens_mapping` в `config.py` используется для мапинга токенов (если вам надо какой-то еще, то просто добавьте
  удобное для вас название и адрес нового токена)

### Примеры использования

Для ввода `from_token`, `to_token`, `from_amount`, `to_amount` (надеюсь по названию понятно что это) используются аргументы командной
строки.

#### Формат команды с аргументами:

`python main.py from_token to_token from_amount to_amount`

1. Первый аргумент: `from_token`, указывает из какого токена делать свапы

2. Второй аргумент: `to_token`, указывает в какой токен делать свапы

3. Третий аргумент: `from_amount`, указывает от какого количества монет делать свапы

4. Четвертый аргумент: `to_amount`, указывает до какого количества монет делать свапы

#### Для свапа от 0.5 до 1 USDT в APT нужно ипользовать команду:

`python main.py USDT APT 0.5 1`

#### Для свапа от 0.7 до 0.9 APT в USDT нужно ипользовать команду:

`python main.py APT USDT 0.7 0.9`

#### Для свапа от 1 до 2.3 USDT в APT нужно ипользовать команду:

`python main.py USDT APT 1 2.3`

### Пример работы

Свап от 0.1 до 0.4 USDT в APT

![alt text](photos/liquidswap-example-updated.png)

### Telegram https://t.me/sybil_v_zakone

_В основе лежит репозиторий: https://github.com/WayneAl/liquidswap-sdk-python_
