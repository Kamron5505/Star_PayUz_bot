# -*- coding: utf-8 -*-
"""
Кэширование для ускорения работы бота
"""

import time
from typing import Any, Dict, List, Optional
import json

class Cache:
    """Простой кэш в памяти"""
    
    def __init__(self, ttl: int = 300):  # 5 минут по умолчанию
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Сохранить значение в кэш"""  
        expire_time = time.time() + (ttl or self.ttl)
        self._cache[key] = {
            'value': value,
            'expire': expire_time
        }
    
    def get(self, key: str) -> Any:
        """Получить значение из кэша"""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if time.time() > item['expire']:
            del self._cache[key]
            return None
        
        return item['value']
    
    def delete(self, key: str) -> None:
        """Удалить значение из кэша"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        self._cache.clear()
    
    def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        if key not in self._cache:
            return False
        
        if time.time() > self._cache[key]['expire']:
            del self._cache[key]
            return False
        
        return True

# Глобальный кэш
cache = Cache(ttl=300)  # 5 минут

# Ключи для кэширования
CACHE_KEYS = {
    'PRODUCTS_BY_CATEGORY': 'products_by_category_{}',
    'ALL_PRODUCTS': 'all_products',
    'USER_DATA': 'user_{}',
    'CATEGORIES': 'categories',
    'STATISTICS': 'statistics',
    'ACTIVE_PROMOCODES': 'active_promocodes'
}

def cache_products_by_category(category: str, products: List) -> None:
    """Кэшировать товары по категории"""
    key = CACHE_KEYS['PRODUCTS_BY_CATEGORY'].format(category)
    cache.set(key, products, ttl=600)  # 10 минут для товаров

def get_cached_products_by_category(category: str) -> Optional[List]:
    """Получить товары по категории из кэша"""
    key = CACHE_KEYS['PRODUCTS_BY_CATEGORY'].format(category)
    return cache.get(key)

def cache_user_data(user_id: int, data: Dict) -> None:
    """Кэшировать данные пользователя"""
    key = CACHE_KEYS['USER_DATA'].format(user_id)
    cache.set(key, data, ttl=1800)  # 30 минут для пользователей

def get_cached_user_data(user_id: int) -> Optional[Dict]:
    """Получить данные пользователя из кэша"""
    key = CACHE_KEYS['USER_DATA'].format(user_id)
    return cache.get(key)

def invalidate_category_cache(category: str = None) -> None:
    """Инвалидировать кэш категорий"""
    if category:
        key = CACHE_KEYS['PRODUCTS_BY_CATEGORY'].format(category)
        cache.delete(key)
    else:
        # Инвалидировать все категории
        for cat in ['premium', 'stars', 'boost', 'gifts', 'virtual_numbers', 'robux']:
            key = CACHE_KEYS['PRODUCTS_BY_CATEGORY'].format(cat)
            cache.delete(key)
    
    # Также инвалидировать общий кэш товаров
    cache.delete(CACHE_KEYS['ALL_PRODUCTS'])

def cache_statistics(stats: Dict) -> None:
    """Кэшировать статистику"""
    cache.set(CACHE_KEYS['STATISTICS'], stats, ttl=60)  # 1 минута для статистики

def get_cached_statistics() -> Optional[Dict]:
    """Получить статистику из кэша"""
    return cache.get(CACHE_KEYS['STATISTICS'])