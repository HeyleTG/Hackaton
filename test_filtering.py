#!/usr/bin/env python3
"""
Тестовый скрипт для демонстрации работы API фильтрации квартир
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_filter_api():
    """Тестирование API фильтрации"""
    print("🔍 Тестирование API фильтрации квартир")
    print("=" * 50)
    
    # Тест 1: Фильтрация по цене
    print("\n1. Фильтрация по цене (от 3 до 5 млн):")
    response = requests.get(f"{BASE_URL}/api/listings/filter", params={
        "min_price": 3000000,
        "max_price": 5000000
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {data['total']} объявлений")
        for listing in data['listings'][:3]:  # Показываем первые 3
            print(f"   - {listing['title']} | {listing['price']:,} ₽")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # Тест 2: Фильтрация по количеству комнат
    print("\n2. Фильтрация по количеству комнат (студия):")
    response = requests.get(f"{BASE_URL}/api/listings/filter", params={
        "rooms": "студия"
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {data['total']} студий")
        for listing in data['listings'][:3]:
            print(f"   - {listing['title']} | {listing['area']} м²")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # Тест 3: Фильтрация по площади
    print("\n3. Фильтрация по площади (от 20 до 40 м²):")
    response = requests.get(f"{BASE_URL}/api/listings/filter", params={
        "min_area": 20,
        "max_area": 40
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {data['total']} объявлений")
        for listing in data['listings'][:3]:
            print(f"   - {listing['title']} | {listing['area']} м²")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # Тест 4: Комбинированная фильтрация
    print("\n4. Комбинированная фильтрация (студия, евроремонт, до 4 млн):")
    response = requests.get(f"{BASE_URL}/api/listings/filter", params={
        "rooms": "студия",
        "finish": "евроремонт",
        "max_price": 4000000
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {data['total']} объявлений")
        for listing in data['listings'][:3]:
            print(f"   - {listing['title']} | {listing['price']:,} ₽ | {listing['remont']}")
    else:
        print(f"   Ошибка: {response.status_code}")

def test_search_api():
    """Тестирование API поиска"""
    print("\n🔍 Тестирование API поиска")
    print("=" * 50)
    
    # Тест 1: Поиск по ключевому слову
    print("\n1. Поиск по слову 'студия':")
    response = requests.get(f"{BASE_URL}/api/listings/search", params={
        "q": "студия"
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {data['total']} объявлений")
        for listing in data['listings'][:3]:
            print(f"   - {listing['title']}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # Тест 2: Поиск по адресу
    print("\n2. Поиск по адресу 'Уральская':")
    response = requests.get(f"{BASE_URL}/api/listings/search", params={
        "q": "Уральская"
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {data['total']} объявлений")
        for listing in data['listings'][:3]:
            print(f"   - {listing['address']}")
    else:
        print(f"   Ошибка: {response.status_code}")

def test_stats_api():
    """Тестирование API статистики"""
    print("\n📊 Тестирование API статистики")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/api/listings/stats")
    if response.status_code == 200:
        data = response.json()
        print(f"Общее количество объявлений: {data['total_listings']}")
        
        print(f"\nСтатистика по ценам:")
        price_stats = data['price_stats']
        print(f"  Минимальная цена: {price_stats['min_price']:,} ₽")
        print(f"  Максимальная цена: {price_stats['max_price']:,} ₽")
        print(f"  Средняя цена: {price_stats['avg_price']:,.0f} ₽")
        
        print(f"\nСтатистика по регионам:")
        for region in data['region_stats'][:5]:
            print(f"  {region['region']}: {region['count']} объявлений")
        
        print(f"\nСтатистика по количеству комнат:")
        for rooms in data['rooms_stats'][:5]:
            print(f"  {rooms['rooms']}: {rooms['count']} объявлений")
    else:
        print(f"Ошибка: {response.status_code}")

def test_router_endpoints():
    """Тестирование эндпоинтов роутера"""
    print("\n🔗 Тестирование эндпоинтов роутера")
    print("=" * 50)
    
    # Тест роутера фильтрации
    print("\n1. Тест роутера /listings/filter:")
    response = requests.get(f"{BASE_URL}/listings/filter", params={
        "min_price": 2000000,
        "max_price": 6000000,
        "rooms": "студия"
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {len(data)} объявлений")
        for listing in data[:2]:
            print(f"   - {listing['title']}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # Тест роутера поиска
    print("\n2. Тест роутера /listings/search:")
    response = requests.get(f"{BASE_URL}/listings/search", params={
        "q": "новый"
    })
    if response.status_code == 200:
        data = response.json()
        print(f"   Найдено: {len(data)} объявлений")
        for listing in data[:2]:
            print(f"   - {listing['title']}")
    else:
        print(f"   Ошибка: {response.status_code}")
    
    # Тест роутера статистики
    print("\n3. Тест роутера /listings/stats:")
    response = requests.get(f"{BASE_URL}/listings/stats")
    if response.status_code == 200:
        data = response.json()
        print(f"   Общее количество: {data['total_listings']}")
        print(f"   Средняя цена: {data['price_stats']['avg_price']:,.0f} ₽")
    else:
        print(f"   Ошибка: {response.status_code}")

if __name__ == "__main__":
    print("🚀 Запуск тестов API фильтрации квартир")
    print("Убедитесь, что сервер запущен на http://localhost:8000")
    print()
    
    try:
        # Тестируем основные API эндпоинты
        test_filter_api()
        test_search_api()
        test_stats_api()
        
        # Тестируем эндпоинты роутера
        test_router_endpoints()
        
        print("\n✅ Все тесты завершены!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к серверу!")
        print("Убедитесь, что сервер запущен: uvicorn app:app --reload")
    except Exception as e:
        print(f"❌ Ошибка: {e}") 