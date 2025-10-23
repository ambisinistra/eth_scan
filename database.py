from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Модель для поисковых запросов
class SearchQuery(db.Model):
    __tablename__ = 'search_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_address = db.Column(db.String(42), nullable=False)
    start_block = db.Column(db.Integer, nullable=False)
    end_block = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связь с транзакциями
    transactions = db.relationship('Transaction', backref='query', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SearchQuery {self.wallet_address} [{self.start_block}-{self.end_block}]>'


# Модель для транзакций
class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer, db.ForeignKey('search_queries.id', ondelete='CASCADE'), nullable=False, index=True)  # ✅ Добавил index=True
    searched_wallet_address = db.Column(db.String(42), nullable=False, index=True)
    hash = db.Column(db.String(66), nullable=False, unique=True, index=True)
    from_address = db.Column(db.String(42), nullable=False)
    to_address = db.Column(db.String(42))
    value = db.Column(db.Numeric(78, 0), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    block_number = db.Column(db.Integer, nullable=False, index=True)
    txreceipt_status = db.Column(db.String(1), nullable=False)
    gas_used = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Transaction {self.hash}>'


# Функция инициализации базы данных
def init_db(app):
    """
    Инициализирует базу данных и создает все таблицы
    """
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")