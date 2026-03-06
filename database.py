# -*- coding: utf-8 -*-
"""
Работа с базой данных с кэшированием
"""
import sqlite3
from datetime import datetime
import config
from cache import cache_products_by_category, get_cached_products_by_category, invalidate_category_cache

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            join_date TEXT,
            is_subscribed INTEGER DEFAULT 0,
            language TEXT DEFAULT 'uz'
        )
    ''')
    
    # Таблица заказов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            amount INTEGER,
            payment_method TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Таблица товаров
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name_uz TEXT,
            name_ru TEXT,
            description_uz TEXT,
            description_ru TEXT,
            price INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, language="uz"):
    """Добавить пользователя"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, join_date, language)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), language))
    
    conn.commit()
    conn.close()

def user_exists(user_id):
    """Проверить существует ли пользователь"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone()[0] > 0
    
    conn.close()
    return exists

def get_user_language(user_id):
    """Получить язык пользователя"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else "uz"

def set_user_language(user_id, language):
    """Установить язык пользователя"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
    
    conn.commit()
    conn.close()

def create_order(user_id, service, amount, payment_method):
    """Создать заказ"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO orders (user_id, service, amount, payment_method, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, service, amount, payment_method, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return order_id

def get_pending_orders():
    """Получить ожидающие заказы"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT o.order_id, o.user_id, u.username, o.service, o.amount, o.payment_method, o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.status = 'pending'
        ORDER BY o.created_at DESC
    ''')
    
    orders = cursor.fetchall()
    conn.close()
    
    return orders

def update_order_status(order_id, status):
    """Обновить статус заказа"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE orders SET status = ? WHERE order_id = ?', (status, order_id))
    
    conn.commit()
    conn.close()

def get_user_count():
    """Получить количество пользователей"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def get_order_info(order_id):
    """Получить информацию о заказе"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id, service, amount FROM orders WHERE order_id = ?', (order_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result

def get_all_users():
    """Получить всех пользователей для рассылки"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id FROM users')
    users = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return users

# Функции для работы с товарами
def add_product(category, name_uz, name_ru, description_uz, description_ru, price):
    """Добавить товар"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (category, name_uz, name_ru, description_uz, description_ru, price, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (category, name_uz, name_ru, description_uz, description_ru, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return product_id

def get_products_by_category(category):
    """Получить товары по категории с кэшированием"""
    # Пробуем получить из кэша
    cached_products = get_cached_products_by_category(category)
    if cached_products is not None:
        return cached_products
    
    # Если нет в кэше, получаем из базы
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT product_id, name_uz, name_ru, description_uz, description_ru, price
        FROM products 
        WHERE category = ? AND is_active = 1
        ORDER BY product_id
    ''', (category,))
    
    products = cursor.fetchall()
    conn.close()
    
    # Сохраняем в кэш
    cache_products_by_category(category, products)
    
    return products

def get_all_products():
    """Получить все товары"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT product_id, category, name_uz, name_ru, description_uz, description_ru, price
        FROM products 
        WHERE is_active = 1
        ORDER BY category, product_id
    ''')
    
    products = cursor.fetchall()
    conn.close()
    
    return products

def update_product(product_id, category=None, name_uz=None, name_ru=None, description_uz=None, description_ru=None, price=None, is_active=None):
    """Обновить товар"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if name_uz is not None:
        updates.append("name_uz = ?")
        params.append(name_uz)
    if name_ru is not None:
        updates.append("name_ru = ?")
        params.append(name_ru)
    if description_uz is not None:
        updates.append("description_uz = ?")
        params.append(description_uz)
    if description_ru is not None:
        updates.append("description_ru = ?")
        params.append(description_ru)
    if price is not None:
        updates.append("price = ?")
        params.append(price)
    if is_active is not None:
        updates.append("is_active = ?")
        params.append(is_active)
    
    if updates:
        params.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE product_id = ?"
        cursor.execute(query, params)
    
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Удалить товар (деактивировать)"""
    update_product(product_id, is_active=0)

def get_product(product_id):
    """Получить информацию о товаре"""
    conn = sqlite3.connect(config.DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT product_id, category, name_uz, name_ru, description_uz, description_ru, price, is_active
        FROM products 
        WHERE product_id = ?
    ''', (product_id,))
    
    product = cursor.fetchone()
    conn.close()
    
    return product

def get_product_name(product_id, lang="uz"):
    """Получить название товара на указанном языке"""
    product = get_product(product_id)
    if product:
        if lang == "uz":
            return product[2]  # name_uz
        else:
            return product[3]  # name_ru
    return f"Товар #{product_id}"
