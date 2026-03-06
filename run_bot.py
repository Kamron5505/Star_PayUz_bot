#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск бота Star_payuz с обычными эмодзи
"""

import asyncio
import logging
from bot import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Запуск бота Star_payuz...")
    print("⭐️ Бот использует обычные эмодзи")
    print("✅ Бот готов к работе!")
    asyncio.run(main())