"""
Примеры использования асинхронного клиента LokisApi.
"""

import asyncio
from lokisapi import AsyncLokisApiClient, ChatMessage, ChatRole, ImageSize, ImageQuality, ImageStyle


async def main():
    # Инициализация асинхронного клиента
    async with AsyncLokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755") as client:
        print("=== Асинхронный клиент LokisApi ===\n")
        
        # Пример 1: Простой чат
        print("1. Простой чат:")
        try:
            messages = [ChatMessage(ChatRole.USER, "Привет! Как дела?")]
            response = await client.chat(messages, model="gpt-5")
            print(f"   Ответ: {response.choices[0]['message']['content']}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()
        
        # Пример 2: Стриминг чата
        print("2. Стриминг чата:")
        try:
            messages = [ChatMessage(ChatRole.USER, "Расскажи короткую историю")]
            print("   Ответ: ", end="")
            async for chunk in await client.chat(messages, model="gpt-5", stream=True):
                if chunk.choices[0].get('delta', {}).get('content'):
                    print(chunk.choices[0]['delta']['content'], end="")
            print("\n")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()
        
        # Пример 3: Генерация изображения
        print("3. Генерация изображения:")
        try:
            response = await client.generate_image_simple(
                prompt="A beautiful sunset over mountains",
                size=ImageSize.SIZE_1024,
                quality=ImageQuality.HD,
                style=ImageStyle.VIVID
            )
            print(f"   URL изображения: {response.data[0]['url']}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()
        
        # Пример 4: Получение моделей
        print("4. Получение моделей:")
        try:
            models = await client.list_models()
            print(f"   Найдено моделей: {len(models)}")
            
            thinking_models = await client.get_thinking_models()
            print(f"   Thinking модели: {thinking_models}")
            
            image_models = await client.get_image_models()
            print(f"   Image модели: {image_models}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()
        
        # Пример 5: Информация о кэше
        print("5. Информация о кэше:")
        try:
            cache_info = await client.get_models_cache_info()
            print(f"   Кэш активен: {cache_info['cached']}")
            print(f"   Возраст кэша: {cache_info['age_seconds']:.0f} секунд")
            print(f"   Количество моделей: {cache_info['models_count']}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()
        
        # Пример 6: Thinking режим
        print("6. Thinking режим:")
        try:
            messages = [ChatMessage(ChatRole.USER, "Реши уравнение: x² + 5x + 6 = 0")]
            response = await client.chat(
                messages=messages,
                model="gemini-2.5-pro",
                thinking=True,
                thinking_budget=2000
            )
            print(f"   Ответ: {response.choices[0]['message']['content']}")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()
        
        # Пример 7: Пакетная обработка изображений
        print("7. Пакетная обработка:")
        try:
            from lokisapi import batch_encode_images, batch_process_images
            
            # Симулируем пакетную обработку
            image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
            print(f"   Обработка {len(image_paths)} изображений...")
            
            # В реальном использовании здесь были бы реальные пути к файлам
            # encoded_images = await batch_encode_images(image_paths)
            # processed_images = await batch_process_images(image_paths, (1024, 1024))
            
            print("   Пакетная обработка завершена")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()


async def concurrent_example():
    """Пример конкурентного выполнения запросов."""
    print("=== Конкурентное выполнение ===\n")
    
    async with AsyncLokisApiClient("sk-cdfa39cefe2df7a0e3d6e6dbf85a31a862b8bd95c8d7975e14cfc353a2d83755") as client:
        # Создаем несколько задач одновременно
        tasks = []
        
        # Задача 1: Получить модели
        tasks.append(client.list_models())
        
        # Задача 2: Простой чат
        messages = [ChatMessage(ChatRole.USER, "Скажи 'Привет'")]
        tasks.append(client.chat(messages, model="gpt-5"))
        
        # Задача 3: Генерация изображения
        tasks.append(client.generate_image_simple("A simple test image"))
        
        # Выполняем все задачи одновременно
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            print("1. Модели:")
            if not isinstance(results[0], Exception):
                print(f"   Найдено: {len(results[0])} моделей")
            else:
                print(f"   Ошибка: {results[0]}")
            
            print("2. Чат:")
            if not isinstance(results[1], Exception):
                print(f"   Ответ: {results[1].choices[0]['message']['content']}")
            else:
                print(f"   Ошибка: {results[1]}")
            
            print("3. Изображение:")
            if not isinstance(results[2], Exception):
                print(f"   URL: {results[2].data[0]['url']}")
            else:
                print(f"   Ошибка: {results[2]}")
                
        except Exception as e:
            print(f"Ошибка конкурентного выполнения: {e}")


if __name__ == "__main__":
    # Запуск основного примера
    asyncio.run(main())
    
    # Запуск примера конкурентного выполнения
    asyncio.run(concurrent_example())
