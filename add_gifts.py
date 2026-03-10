# -*- coding: utf-8 -*-
"""
Добавление подарков в базу данных
"""
import sqlite3
import database
import config

# Инициализируем базу данных если нужно
database.init_db()

# Сначала удаляем все старые подарки
print("🗑️ Удаляем старые подарки...")
conn = sqlite3.connect(config.DATABASE_FILE)
cursor = conn.cursor()
cursor.execute("DELETE FROM products WHERE category = 'gifts'")
conn.commit()
conn.close()
print("✅ Старые подарки удалены!")

# Подарки с эмодзи (точно по твоему списку)
gifts = [
    # 15 stars подарки (4,000 uzs)
    ("💝 | 15 ⭐️ Gift", "💝 | 15 ⭐️ Gift", 
     "15 stars подарок", "15 stars подарок", 
     4000),
    ("🧸 | 15 ⭐️ Gift", "🧸 | 15 ⭐️ Gift",
     "15 stars подарок", "15 stars подарок",
     4000),
    
    # 25 stars подарки (6,000 uzs)
    ("🎁 | 25 ⭐️ Gift", "🎁 | 25 ⭐️ Gift",
     "25 stars подарок", "25 stars подарок",
     6000),
    ("🌹 | 25 ⭐️ Gift", "🌹 | 25 ⭐️ Gift",
     "25 stars подарок", "25 stars подарок",
     6000),
    
    # 50 stars подарки (13,000 uzs)
    ("🎂 | 50 ⭐️ Gift", "🎂 | 50 ⭐️ Gift",
     "50 stars подарок", "50 stars подарок",
     13000),
    ("🚀 | 50 ⭐️ Gift", "🚀 | 50 ⭐️ Gift",
     "50 stars подарок", "50 stars подарок",
     13000),
    ("🍾 | 50 ⭐️ Gift", "🍾 | 50 ⭐️ Gift",
     "50 stars подарок", "50 stars подарок",
     13000),
    ("💐 | 50 ⭐️ Gift", "💐 | 50 ⭐️ Gift",
     "50 stars подарок", "50 stars подарок",
     13000),
    
    # 100 stars подарки (22,000 uzs)
    ("💎 | 100 ⭐️ Gift", "💎 | 100 ⭐️ Gift",
     "100 stars подарок", "100 stars подарок",
     22000),
    ("🏆 | 100 ⭐️ Gift", "🏆 | 100 ⭐️ Gift",
     "100 stars подарок", "100 stars подарок",
     22000),
    ("💍 | 100 ⭐️ Gift", "💍 | 100 ⭐️ Gift",
     "100 stars подарок", "100 stars подарок",
     22000),
]

print("\n📦 Добавляем новые подарки...")
# Добавляем подарки
for name_uz, name_ru, desc_uz, desc_ru, price in gifts:
    database.add_product(
        category="gifts",
        name_uz=name_uz,
        name_ru=name_ru,
        description_uz=desc_uz,
        description_ru=desc_ru,
        price=price
    )
    print(f"✅ Добавлен: {name_uz} - {price:,} uzs")

print("\n✅ Все 11 подарков добавлены!")
print("Теперь в категории Gifts только эти подарки.")
