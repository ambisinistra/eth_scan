from flask import Flask, render_template, request, redirect, url_for, session
from utils import validate_block_numbers, determine_transaction_type
from database import db, init_db, SearchQuery, Transaction  # ✅ Добавляем импорт моделей
from sqlalchemy.dialects.postgresql import insert

import requests
import json

from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

# Загрузка данных из файла
def load_transactions():
    with open('result.txt', 'r') as f:
        transactions = json.load(f)
    return transactions

# Конвертация wei в ETH
def wei_to_eth(wei_value):
    return float(wei_value) / 1e18 if wei_value else 0

# Конвертация timestamp в читаемую дату
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

def get_latest_block_number(api_key=None):
    # Если ключ не передан, берём из переменных окружения
    if api_key is None:
        api_key = os.getenv("ETHERSCAN_API_KEY")
        if not api_key:
            print("Ошибка: API ключ не найден в переменных окружения")
            return None
        
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainid": 1,
        "module": "proxy",
        "action": "eth_blockNumber",
        "apikey": api_key
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    # Пример ответа:
    # {
    #   "jsonrpc":"2.0",
    #   "id":1,
    #   "result":"0x10d4f"    <-- блок в hex
    # }
    if "result" in data:
        hex_block = data["result"]
        try:
            block_int = int(hex_block, 16)
        except ValueError:
            raise RuntimeError("Не удалось распознать hex блока: " + hex_block)
        return block_int
    else:
        # обработка ошибок
        raise RuntimeError("Ошибка ответа Etherscan или поле result отсутствует: " + str(data))

app = Flask(__name__)

# ✅ Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://usr:pass@psql:5432/lets_goto_it'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# ✅ Инициализация расширения SQLAlchemy
db.init_app(app)

# ✅ Создание таблиц при запуске
init_db(app)

def fetch_etherscan_transactions(address, start_block, end_block, api_key=None):
    """
    Получает список транзакций для указанного адреса через Etherscan API.

    Args:
        address: Адрес Ethereum кошелька
        start_block: Начальный блок
        end_block: Конечный блок
        api_key: API ключ Etherscan

    Returns:
        Путь к сохранённому файлу или None в случае ошибки
    """

    # Если ключ не передан, берём из переменных окружения
    if api_key is None:
        api_key = os.getenv("ETHERSCAN_API_KEY")
        if not api_key:
            print("Ошибка: API ключ не найден в переменных окружения")
            return None


    url = (
        "https://api.etherscan.io/v2/api"
        f"?chainid=1"
        f"&module=account"
        f"&action=txlist"
        f"&address={address}"
        f"&startblock={start_block}"
        f"&endblock={end_block}"
        "&sort=asc"
        f"&apikey={api_key}"
    )

    response = requests.get(url)
    data = response.json()

    if data.get("status") == "1" or data.get("message") == "OK":
        os.makedirs("cache", exist_ok=True)
        filename = f"cache/{address}_{start_block}_{end_block}.json"

        with open(filename, "w") as f:
            json.dump(data["result"], f, indent=2)

        print(f"Сохранено {len(data['result'])} транзакций в {filename}")
        # ✅ Сохраняем в базу данных
        if True:
            # 1. Создаём запись в search_queries
            search_query = SearchQuery(
                wallet_address=address,
                start_block=start_block,
                end_block=end_block
            )
            db.session.add(search_query)
            db.session.flush()  # Получаем id, не коммитя транзакцию
            
            # Загружаем транзакции из файла
            with open(filename, 'r') as f:
                transactions = json.load(f)

            # 2. Подготавливаем данные для bulk insert
            transactions_data = []
            for tx in transactions:
                transactions_data.append({
                    'query_id': search_query.id,
                    'searched_wallet_address': address,
                    'hash': tx['hash'],
                    'from_address': tx['from'],
                    'to_address': tx.get('to', ''),
                    'value': int(tx['value']),
                    'timestamp': datetime.fromtimestamp(int(tx['timeStamp'])),
                    'block_number': int(tx['blockNumber']),
                    'txreceipt_status': tx['txreceipt_status'],
                    'gas_used': int(tx['gasUsed']),
                    'transaction_type': determine_transaction_type(tx)
                })
            
            # 3. Используем INSERT ... ON CONFLICT DO NOTHING
            if transactions_data:
                stmt = insert(Transaction).values(transactions_data)
                stmt = stmt.on_conflict_do_nothing(index_elements=['hash'])
                db.session.execute(stmt)
            
            # 3. Коммитим всё вместе
            db.session.commit()
            
        #except Exception as e:
        #    db.session.rollback()  # Откатываем изменения при ошибке
        #    print(f"❌ Ошибка при сохранении в БД: {e}")
            # Продолжаем работу - файл уже сохранён
        return len(data['result'])
    elif data.get("message") == "No transactions found":
        # Treat as valid case with empty result
        os.makedirs("cache", exist_ok=True)
        filename = f"cache/{address}_{start_block}_{end_block}.json"
        
        with open(filename, "w") as f:
            json.dump([], f, indent=2)
        
        print(f"No transactions found for address {address}")
        return 0
    else:
        error_message = data.get("message", "Unknown error")
        raise RuntimeError(f"Etherscan API error: {error_message}. Full response: {data}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        wallet_address = request.form.get('wallet_address')
        start_block = int(request.form.get('start_block'))
        end_block = int(request.form.get('end_block'))
        validate_block_numbers(start_block, end_block)
        
        #check rast ETH block possible now if it's modern and not historical search
        if end_block > 23632440:
            last_block_n = get_latest_block_number()
            # Check if API call succeeded
            if last_block_n is None:
                raise RuntimeError ("Error: Could not fetch latest block number from Etherscan")

            if end_block is None:
                end_block = last_block_n
            else:
                end_block = min(end_block, last_block_n)
        num_transactions = fetch_etherscan_transactions(wallet_address, start_block, end_block)

        if num_transactions:
            return redirect(url_for('transactions',
                      wallet_address=wallet_address,
                      start_block=start_block,
                      end_block=end_block))
        else:
            return "There is no transactions for the requested wallet in the requested period of time", 200
    
    return render_template('input_form.html')

@app.route('/transactions')
def transactions():
    # Получаем имя файла из сессии
    wallet_address = request.args.get('wallet_address')
    start_block = request.args.get('start_block')
    end_block = request.args.get('end_block')
    filename = f"cache/{wallet_address}_{start_block}_{end_block}.json"
    if not filename or not os.path.exists(filename):
        return redirect(url_for('index'))
    
    # Получаем номер страницы
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # ✅ Загружаем транзакции из базы данных (новый синтаксис Flask-SQLAlchemy 3.x)
    query = db.session.query(Transaction).filter(
        Transaction.searched_wallet_address == wallet_address,
        Transaction.block_number >= start_block,
        Transaction.block_number <= end_block
    ).order_by(Transaction.block_number.desc())
    
    # Получаем общее количество
    total = query.count()
    
    # Пагинация
    transactions_page = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # ✅ Обрабатываем данные - используем точку вместо квадратных скобок!
    processed_txs = []
    for tx in transactions_page:
        processed_txs.append({
            'hash': tx.hash,                    # ✅ Было: tx['hash']
            'from': tx.from_address,            # ✅ Было: tx['from']
            'to': tx.to_address or '',          # ✅ Было: tx['to']
            'value_eth': wei_to_eth(str(tx.value)),  # ✅ Было: tx['value']
            'timestamp': tx.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # ✅ Уже datetime объект
            'block': tx.block_number,           # ✅ Было: tx['blockNumber']
            'status': 'Success' if tx.txreceipt_status == '1' else 'Failed',  # ✅
            'type': tx.transaction_type,        # ✅ Было: tx['type']
            'gas_used': tx.gas_used,            # ✅ Было: tx['gasUsed']
        })
    
    # Параметры пагинации
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('transactions.html',
                            transactions=processed_txs,
                            page=page,
                            total_pages=total_pages,
                            has_prev=has_prev,
                            has_next=has_next,
                            total=total,
                            wallet_address=wallet_address,
                            start_block=start_block,      
                            end_block=end_block,          
                            filename=filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)