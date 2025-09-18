# LokisApi Python Library

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/lokisapi.svg)](https://pypi.org/project/lokisapi/)

Профессиональная Python библиотека для взаимодействия с LokisApi - мощным API для генерации изображений и чат-комплетаций.

## 🚀 Возможности

- **Генерация изображений** с помощью DALL-E моделей
- **Редактирование изображений** с поддержкой DALL-E
- **Чат-комплетации** с поддержкой GPT и Gemini моделей
- **Thinking режим** для Gemini 2.5 моделей
- **Reasoning Effort** для GPT-5 моделей
- **Стриминг ответов** для реального времени
- **Автоматическое получение моделей** из API с кэшированием
- **Умное управление моделями** - фильтрация по категориям и возможностям
- **Обработка изображений** - кодирование, декодирование, изменение размера
- **Расширенная обработка ошибок** с детальными исключениями и лимитами
- **Простой и интуитивный API** в стиле OpenAI
- **Полная совместимость** с LokisApi endpoints
- **Поддержка всех моделей** из вашего API без обновления библиотеки

## 📦 Установка

```bash
pip install lokisapi
```

Или из исходного кода:

```bash
git clone https://github.com/masezev/lokisapi-python.git
cd lokisapi-python
pip install -e .
```

## 🔑 Быстрый старт

### Инициализация клиента

```python
from lokisapi import LokisApiClient

# Инициализация с вашим API ключом
client = LokisApiClient("YOUR_API_KEY")
```

### Чат-комплетации

```python
from lokisapi import ChatMessage, ChatRole

# Простой чат
messages = [
    ChatMessage(ChatRole.USER, "Привет! Как дела?")
]
response = client.chat(messages, model="gpt-5")
print(response.choices[0]['message']['content'])
```

### Стриминг чат-комплетаций

```python
# Стриминг ответов
messages = [ChatMessage(ChatRole.USER, "Расскажи историю")]
for chunk in client.chat(messages, model="gpt-5", stream=True):
    if chunk.choices[0].get('delta', {}).get('content'):
        print(chunk.choices[0]['delta']['content'], end='')
```

### Генерация изображений

```python
from lokisapi import ImageGenerationRequest, ImageSize, ImageQuality, ImageStyle

# Простая генерация
response = client.generate_image_simple(
    prompt="A beautiful sunset over mountains",
    size=ImageSize.SIZE_1024,
    quality=ImageQuality.HD,
    style=ImageStyle.VIVID
)
print(response.data[0]['url'])

# Расширенная генерация
request = ImageGenerationRequest(
    prompt="A futuristic city with flying cars",
    model="dall-e-3",
    size=ImageSize.SIZE_1024,
    quality=ImageQuality.HD,
    style=ImageStyle.VIVID
)
response = client.generate_image(request)
```

### Редактирование изображений

```python
from lokisapi import ImageEditRequest, encode_image_to_base64

# Кодируем изображение в base64
image_base64 = encode_image_to_base64("path/to/image.jpg")

# Редактируем изображение
response = client.edit_image_simple(
    image=image_base64,
    prompt="Add a rainbow to the sky",
    size=ImageSize.SIZE_1024
)
print(response.data[0]['url'])
```

### Thinking режим (Gemini 2.5)

```python
from lokisapi import THINKING_MODELS

# Использование Thinking режима
messages = [ChatMessage(ChatRole.USER, "Реши сложную математическую задачу")]
response = client.chat(
    messages=messages,
    model="gemini-2.5-pro",
    thinking=True,
    thinking_budget=2000
)
print(response.choices[0]['message']['content'])

# Модели с поддержкой Thinking
print(f"Models with Thinking: {THINKING_MODELS}")
```

### Reasoning Effort (GPT-5)

```python
from lokisapi import ReasoningEffort

# Использование Reasoning Effort
messages = [ChatMessage(ChatRole.USER, "Объясни квантовую физику")]
response = client.chat(
    messages=messages,
    model="gpt-5",
    reasoning_effort=ReasoningEffort.HIGH
)
print(response.choices[0]['message']['content'])
```

### Автоматическое получение моделей

```python
# Получить все доступные модели (автоматически кэшируются)
models = client.list_models()
for model in models:
    print(f"{model.id} - {model.owned_by}")

# Получить информацию о конкретной модели
model = client.get_model("gpt-5")
print(f"Model: {model.id}, Created: {model.created}")

# Получить модели по категориям
text_models = client.get_models_by_category("text")
image_models = client.get_models_by_category("image")
thinking_models = client.get_models_by_category("thinking")

# Получить модели с определенными возможностями
thinking_models = client.get_thinking_models()
image_models = client.get_image_models()
text_models = client.get_text_models()

# Информация о кэше
cache_info = client.get_models_cache_info()
print(f"Models cached: {cache_info['cached']}")
print(f"Cache age: {cache_info['age_seconds']} seconds")

# Принудительное обновление кэша
client.refresh_models_cache()
```

## 📚 Подробная документация

### LokisApiClient

Основной класс для взаимодействия с LokisApi.

#### Конструктор

```python
LokisApiClient(api_key: str, base_url: str = "https://lokisapi.online/v1", model_cache_duration: float = 3600)
```

- `api_key`: Ваш API ключ LokisApi
- `base_url`: Базовый URL API (по умолчанию: https://lokisapi.online/v1)
- `model_cache_duration`: Длительность кэша моделей в секундах (по умолчанию: 3600 = 1 час)

#### Методы

##### `chat(messages, model="gpt-5", temperature=1.0, max_tokens=None, stream=False)`

Удобный метод для чат-комплетаций.

**Параметры:**
- `messages`: Список сообщений `ChatMessage`
- `model`: Модель для использования (по умолчанию: "gpt-5")
- `temperature`: Температура сэмплирования (0.0-2.0)
- `max_tokens`: Максимальное количество токенов
- `stream`: Включить стриминг

**Возвращает:**
- `ChatCompletionResponse` или `Iterator[ChatCompletionChunk]` при стриминге

##### `generate_image_simple(prompt, size="1024x1024", model="dall-e-3")`

Удобный метод для простой генерации изображений.

**Параметры:**
- `prompt`: Промпт для генерации изображения
- `size`: Размер изображения
- `model`: Модель для использования

**Возвращает:**
- `ImageGenerationResponse`

##### `list_models(force_refresh=False)`

Получить список всех доступных моделей (автоматически кэшируются).

**Параметры:**
- `force_refresh`: Принудительно обновить кэш из API

**Возвращает:**
- `List[Model]`

##### `get_model(model_id, force_refresh=False)`

Получить информацию о конкретной модели.

**Параметры:**
- `model_id`: ID модели
- `force_refresh`: Принудительно обновить кэш из API

**Возвращает:**
- `Model`

##### `get_thinking_models(force_refresh=False)`

Получить список моделей с поддержкой Thinking (Gemini 2.5).

**Возвращает:**
- `List[str]` - список ID моделей

##### `get_image_models(force_refresh=False)`

Получить список моделей для генерации изображений.

**Возвращает:**
- `List[str]` - список ID моделей

##### `get_text_models(force_refresh=False)`

Получить список моделей для текстовых задач.

**Возвращает:**
- `List[str]` - список ID моделей

##### `get_models_by_category(category, force_refresh=False)`

Получить модели по категории.

**Параметры:**
- `category`: Категория ("text", "image", "thinking", "deprecated")
- `force_refresh`: Принудительно обновить кэш из API

**Возвращает:**
- `List[Model]`

##### `refresh_models_cache()`

Принудительно обновить кэш моделей из API.

##### `clear_models_cache()`

Очистить кэш моделей.

##### `get_models_cache_info()`

Получить информацию о состоянии кэша моделей.

**Возвращает:**
- `Dict[str, Any]` - информация о кэше

### Модели данных

#### ChatMessage

```python
@dataclass
class ChatMessage:
    role: ChatRole  # system, user, assistant
    content: str
```

#### ImageGenerationRequest

```python
@dataclass
class ImageGenerationRequest:
    prompt: str
    model: str = "dall-e-3"
    n: int = 1
    size: ImageSize = ImageSize.SIZE_1024
    quality: str = "standard"
    style: str = "vivid"
```

#### ChatCompletionRequest

```python
@dataclass
class ChatCompletionRequest:
    messages: List[ChatMessage]
    model: str = "gpt-5"
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    stream: bool = False
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[Union[str, List[str]]] = None
```

### Утилиты для работы с изображениями

```python
from lokisapi import (
    encode_image_to_base64, decode_base64_to_image, 
    save_base64_image, resize_image_for_api, validate_image_size
)

# Кодирование изображения в base64
base64_image = encode_image_to_base64("path/to/image.jpg")

# Декодирование base64 в PIL Image
image = decode_base64_to_image(base64_image)

# Сохранение base64 изображения в файл
save_base64_image(base64_image, "output.png")

# Изменение размера изображения для API
resized_base64 = resize_image_for_api("large_image.jpg", (1024, 1024))

# Проверка размера изображения
is_valid = validate_image_size("1024x1024")  # True
```

### Утилиты для работы с моделями

```python
from lokisapi import (
    format_model_info, get_supported_models, 
    estimate_tokens, validate_api_key_format
)

# Информация о модели
info = format_model_info("gpt-5")
print(f"Model: {info['name']}, Provider: {info['provider']}")

# Получение поддерживаемых моделей
text_models = get_supported_models("text")
image_models = get_supported_models("image")

# Оценка токенов
tokens = estimate_tokens("Hello, world!")  # Примерно 3-4 токена

# Проверка формата API ключа
is_valid = validate_api_key_format("sk-...")  # True
```

### Исключения

Библиотека предоставляет расширенную систему исключений для обработки ошибок:

#### Основные исключения
- `LokisApiError`: Базовое исключение для всех ошибок LokisApi
- `AuthenticationError`: Ошибка аутентификации (неверный API ключ)
- `RateLimitError`: Превышен лимит запросов
- `APIError`: Общая ошибка API
- `ValidationError`: Ошибка валидации входных данных
- `NetworkError`: Сетевая ошибка (таймаут, соединение)

#### Специализированные исключения
- `ModelNotFoundError`: Модель не найдена
- `ModelNotSupportedError`: Модель не поддерживает запрашиваемую функцию
- `QuotaExceededError`: Превышена квота (наследует от RateLimitError)
- `TokenLimitError`: Превышен лимит токенов (наследует от RateLimitError)
- `RequestLimitError`: Превышен лимит запросов (наследует от RateLimitError)
- `ServiceUnavailableError`: Сервис временно недоступен
- `ImageProcessingError`: Ошибка обработки изображения

```python
from lokisapi import (
    LokisApiClient, AuthenticationError, RateLimitError, 
    QuotaExceededError, TokenLimitError, ModelNotFoundError
)

try:
    client = LokisApiClient("invalid-key")
    response = client.chat(messages)
except AuthenticationError as e:
    print(f"Ошибка аутентификации: {e}")
except QuotaExceededError as e:
    print(f"Превышена квота: {e}")
    if e.retry_after:
        print(f"Повторить через {e.retry_after} секунд")
except TokenLimitError as e:
    print(f"Превышен лимит токенов: {e}")
except ModelNotFoundError as e:
    print(f"Модель не найдена: {e.model_id}")
except RateLimitError as e:
    print(f"Превышен лимит: {e}")
    if e.retry_after:
        print(f"Повторить через {e.retry_after} секунд")
```

## 🎯 Примеры использования

### Продвинутый чат с контекстом

```python
from lokisapi import LokisApiClient, ChatMessage, ChatRole

client = LokisApiClient("YOUR_API_KEY")

# Создание диалога с системным сообщением
messages = [
    ChatMessage(ChatRole.SYSTEM, "Ты - полезный ассистент, который отвечает на русском языке."),
    ChatMessage(ChatRole.USER, "Объясни, что такое машинное обучение простыми словами.")
]

response = client.chat(messages, model="gpt-5", temperature=0.7)
print(response.choices[0]['message']['content'])
```

### Пакетная генерация изображений

```python
prompts = [
    "A serene mountain landscape at sunrise",
    "A bustling city street at night",
    "A peaceful garden with blooming flowers"
]

for i, prompt in enumerate(prompts):
    print(f"Generating image {i+1}/{len(prompts)}: {prompt}")
    response = client.generate_image_simple(prompt)
    print(f"Image URL: {response.data[0]['url']}")
```

### Стриминг с сохранением в файл

```python
messages = [ChatMessage(ChatRole.USER, "Напиши рассказ о роботе")]

with open("story.txt", "w", encoding="utf-8") as f:
    f.write("=== AI Story ===\n\n")
    
    for chunk in client.chat(messages, model="gpt-5", stream=True):
        if chunk.choices[0].get('delta', {}).get('content'):
            content = chunk.choices[0]['delta']['content']
            f.write(content)
            f.flush()
```

### Пакетная генерация изображений

```python
from lokisapi import ImageSize, ImageQuality, ImageStyle

prompts = [
    "A serene mountain landscape at sunrise",
    "A bustling city street at night", 
    "A peaceful garden with blooming flowers"
]

for i, prompt in enumerate(prompts, 1):
    print(f"Generating image {i}/{len(prompts)}: {prompt}")
    response = client.generate_image_simple(
        prompt=prompt,
        size=ImageSize.SIZE_1024,
        quality=ImageQuality.HD,
        style=ImageStyle.VIVID
    )
    print(f"Image URL: {response.data[0]['url']}")
```

### Работа с Thinking режимом

```python
# Сложная математическая задача с Thinking
messages = [ChatMessage(ChatRole.USER, "Реши уравнение: x² + 5x + 6 = 0")]
response = client.chat(
    messages=messages,
    model="gemini-2.5-pro",
    thinking=True,
    thinking_budget=2000
)
print(response.choices[0]['message']['content'])
```

### Редактирование изображений

```python
from lokisapi import encode_image_to_base64, ImageSize

# Загружаем и редактируем изображение
image_base64 = encode_image_to_base64("original_image.jpg")
response = client.edit_image_simple(
    image=image_base64,
    prompt="Add a beautiful sunset in the background",
    size=ImageSize.SIZE_1024
)
print(f"Edited image: {response.data[0]['url']}")
```

## 🔧 Конфигурация

### Переменные окружения

Вы можете использовать переменные окружения для настройки:

```bash
export LOKISAPI_API_KEY="your-api-key"
export LOKISAPI_BASE_URL="https://lokisapi.online/v1"
```

```python
import os
from lokisapi import LokisApiClient

client = LokisApiClient(
    api_key=os.getenv("LOKISAPI_API_KEY"),
    base_url=os.getenv("LOKISAPI_BASE_URL", "https://lokisapi.online/v1")
)
```

### Настройка таймаутов и повторных попыток

```python
import requests
from lokisapi import LokisApiClient

# Создание клиента с кастомной сессией
session = requests.Session()
session.timeout = 30  # 30 секунд таймаут

client = LokisApiClient("YOUR_API_KEY")
client.session = session
```

## 🧪 Тестирование

```bash
# Установка зависимостей для разработки
pip install -e ".[dev]"

# Запуск тестов
pytest

# Проверка стиля кода
black lokisapi/
flake8 lokisapi/

# Проверка типов
mypy lokisapi/
```

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие библиотеки! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

- **Issues**: [GitHub Issues](https://github.com/masezev/lokisapi-python/issues)
- **Email**: support@lokisapi.online

## 🤖 Доступные модели

### Gemini модели (Google)
- **gemini-2.5-pro** - Самая мощная модель с поддержкой Thinking
- **gemini-2.5-flash** - Быстрая модель с поддержкой Thinking  
- **gemini-2.5-flash-lite** - Облегченная версия с поддержкой Thinking
- **gemini-2.0-flash** - Быстрая модель без Thinking
- **gemini-2.0-flash-lite** - Облегченная версия без Thinking

### OpenAI модели
- **gpt-5** - Самая мощная модель с Reasoning Effort
- **gpt-5-mini** - Компактная версия GPT-5
- **gpt-5-nano** - Минимальная версия GPT-5
- **gpt-4.1** - Улучшенная версия GPT-4
- **gpt-4.1-mini** - Компактная версия GPT-4.1
- **gpt-4.1-nano** - Минимальная версия GPT-4.1
- **gpt-4-turbo** - Быстрая версия GPT-4
- **gpt-4o** - Мультимодальная модель
- **gpt-4o-mini** - Компактная мультимодальная модель
- **o3** - Модель с рассуждениями
- **o3-mini** - Компактная модель с рассуждениями
- **gpt-3.5-turbo** - Быстрая и экономичная модель

### Модели для изображений
- **dall-e-3** - Генерация и редактирование изображений

## 🆕 История изменений

### v1.0.0 (2025-01-XX)
- **Первый релиз** с полной поддержкой LokisApi
- **Чат-комплетации** с поддержкой GPT и Gemini моделей
- **Генерация изображений** с помощью DALL-E моделей
- **Редактирование изображений** с поддержкой DALL-E
- **Thinking режим** для Gemini 2.5 моделей
- **Reasoning Effort** для GPT-5 моделей
- **Стриминг ответов** для реального времени
- **Автоматическое получение моделей** из API с кэшированием
- **Умное управление моделями** - фильтрация по категориям и возможностям
- **Расширенная обработка ошибок** с детальными исключениями и лимитами
- **Утилиты для работы с изображениями** - кодирование, декодирование, изменение размера
- **Полная совместимость** с LokisApi endpoints
- **Поддержка всех моделей** без обновления библиотеки
- **Подробная документация** и примеры использования

---

**Сделано с ❤️ командой LokisApi**

