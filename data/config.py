from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')  # Забираем значение типа str
ADMINS = env.list('ADMINS')  # Тут у нас будет список из админов
IP = env.str('ip')  # Тоже str, но для айпи адреса хоста


# Параметры подключения к БД Postgres
PG_HOST = env.str('PG_HOST')
PG_USER = env.str('PG_USER')
PG_PASS = env.str('PG_PASS')
DB_NAME = env.str('DB_NAME')
HOST = 'localhost'

# Операторы тех. поддержки
SUPPORT_IDS = [
    '1027394288',
]

# Параметры для работы с оплатой Sberbank
PAYMENT_TOKEN = env.str('PAYMENT_TOKEN')

# Параметры для работы с оплатой QIWI
QIWI_TOKEN = env.str('qiwi')
WALLET_QIWI = env.str('wallet')
QIWI_PUBKEY = env.str('qiwi_p_pub')

# Параметры для работы с оплатой Bitcoin
BLOCKCYPHER_TOKEN = env.str('BLOCKCYPHER')
WALLET_BTC = env.str('wallet_btc')
REQUEST_LINK = 'bitcoin:{address}?' \
               'amount={amount}' \
               '&label={message}'

CHANNELS = [
    '-1001547355516',
]

ALLOWED_USERS = [
    # '1027394288',
]

INVITE_CODES = [
    '88888',
    '77777',
    'Rocky'
]
