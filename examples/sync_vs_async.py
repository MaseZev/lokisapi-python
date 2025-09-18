"""
Сравнение синхронного и асинхронного использования LokisApi.
"""

import time
import asyncio
from lokisapi import (
    LokisApiClient, AsyncLokisApiClient, 
    ChatMessage, ChatRole, ImageSize, ImageQuality, ImageStyle
)


def sync_example():
    """Синхронный пример."""
    print("=== Синхронный клиент ===")
    start_time = time.time()
    
    client = LokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755")
    
    # Получение моделей
    models = client.list_models()
    print(f"Модели: {len(models)} найдено")
    
    # Простой чат
    messages = [ChatMessage(ChatRole.USER, "Привет!")]
    response = client.chat(messages, model="gpt-5")
    print(f"Чат: {response.choices[0]['message']['content'][:50]}...")
    
    # Генерация изображения
    image_response = client.generate_image_simple("A beautiful landscape")
    print(f"Изображение: {image_response.data[0]['url'][:50]}...")
    
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд\n")


async def async_example():
    """Асинхронный пример."""
    print("=== Асинхронный клиент ===")
    start_time = time.time()
    
    async with AsyncLokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755") as client:
        # Получение моделей
        models = await client.list_models()
        print(f"Модели: {len(models)} найдено")
        
        # Простой чат
        messages = [ChatMessage(ChatRole.USER, "Привет!")]
        response = await client.chat(messages, model="gpt-5")
        print(f"Чат: {response.choices[0]['message']['content'][:50]}...")
        
        # Генерация изображения
        image_response = await client.generate_image_simple("A beautiful landscape")
        print(f"Изображение: {image_response.data[0]['url'][:50]}...")
    
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд\n")


async def concurrent_async_example():
    """Асинхронный пример с конкурентным выполнением."""
    print("=== Асинхронный клиент (конкурентно) ===")
    start_time = time.time()
    
    async with AsyncLokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755") as client:
        # Выполняем все операции одновременно
        models_task = client.list_models()
        
        messages = [ChatMessage(ChatRole.USER, "Привет!")]
        chat_task = client.chat(messages, model="gpt-5")
        
        image_task = client.generate_image_simple("A beautiful landscape")
        
        # Ждем завершения всех задач
        models, response, image_response = await asyncio.gather(
            models_task, chat_task, image_task
        )
        
        print(f"Модели: {len(models)} найдено")
        print(f"Чат: {response.choices[0]['message']['content'][:50]}...")
        print(f"Изображение: {image_response.data[0]['url'][:50]}...")
    
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд\n")


def sync_concurrent_example():
    """Синхронный пример с 'конкурентным' выполнением (последовательно)."""
    print("=== Синхронный клиент (последовательно) ===")
    start_time = time.time()
    
    client = LokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755")
    
    # Выполняем операции последовательно
    models = client.list_models()
    print(f"Модели: {len(models)} найдено")
    
    messages = [ChatMessage(ChatRole.USER, "Привет!")]
    response = client.chat(messages, model="gpt-5")
    print(f"Чат: {response.choices[0]['message']['content'][:50]}...")
    
    image_response = client.generate_image_simple("A beautiful landscape")
    print(f"Изображение: {image_response.data[0]['url'][:50]}...")
    
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд\n")


async def streaming_comparison():
    """Сравнение стриминга в синхронном и асинхронном режимах."""
    print("=== Сравнение стриминга ===\n")
    
    # Синхронный стриминг
    print("Синхронный стриминг:")
    start_time = time.time()
    
    client = LokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755")
    messages = [ChatMessage(ChatRole.USER, "Расскажи короткую историю")]
    
    print("Ответ: ", end="")
    for chunk in client.chat(messages, model="gpt-5", stream=True):
        if chunk.choices[0].get('delta', {}).get('content'):
            print(chunk.choices[0]['delta']['content'], end="")
    print()
    
    end_time = time.time()
    print(f"Время: {end_time - start_time:.2f} секунд\n")
    
    # Асинхронный стриминг
    print("Асинхронный стриминг:")
    start_time = time.time()
    
    async with AsyncLokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755") as client:
        messages = [ChatMessage(ChatRole.USER, "Расскажи короткую историю")]
        
        print("Ответ: ", end="")
        async for chunk in await client.chat(messages, model="gpt-5", stream=True):
            if chunk.choices[0].get('delta', {}).get('content'):
                print(chunk.choices[0]['delta']['content'], end="")
        print()
    
    end_time = time.time()
    print(f"Время: {end_time - start_time:.2f} секунд\n")


def main():
    """Основная функция для запуска всех примеров."""
    print("Сравнение синхронного и асинхронного использования LokisApi\n")
    
    # Синхронные примеры
    sync_example()
    sync_concurrent_example()
    
    # Асинхронные примеры
    asyncio.run(async_example())
    asyncio.run(concurrent_async_example())
    
    # Сравнение стриминга
    asyncio.run(streaming_comparison())
    
    print("=== Рекомендации ===")
    print("• Используйте синхронный клиент для простых скриптов и интерактивных приложений")
    print("• Используйте асинхронный клиент для:")
    print("  - Веб-приложений (FastAPI, Django)")
    print("  - Высокопроизводительных приложений")
    print("  - Пакетной обработки множества запросов")
    print("  - Когда нужно выполнять несколько операций одновременно")
    print("• Асинхронный клиент особенно эффективен при конкурентном выполнении операций")


if __name__ == "__main__":
    main()
