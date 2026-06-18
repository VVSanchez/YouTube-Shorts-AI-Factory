# 🎬 YouTube Shorts AI Factory

**Multi-Agent система для автоматического создания вирусных YouTube Shorts**

От идеи до готового видео за 2 минуты. Один промпт — 40-секундный вертикальный ролик с субтитрами, музыкой и кинематографичным визуалом.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Working-orange.svg)

---

##  Что это такое

**YouTube Shorts AI Factory** — это фабрика контента на базе multi-agent архитектуры. Система из 7 AI-агентов работает как слаженная команда:

🔍 Аналитик → Креатор → 📝 Сценарист → 🎨 Визуальный директор ↓ 📤 Publisher ← ️ Монтажер ← 🎵 Композитор ← 🖼️ Генератор ← ️ Диктор


Каждый агент — это специализированный LLM-промпт со своей ролью, который передаёт результат следующему.

---

## 🚀 Быстрый старт
```
### 1. Установка


git clone https://github.com/ТВОЙ_НИК/youtube-shorts-ai-factory.git
cd youtube-shorts-ai-factory
pip install -r requirements.txt

### 2. Настройка API ключей

Скопируй `.env.example` в `.env` и заполни ключи:
cp .env.example .env
Минимально нужен только **DeepSeek API** — остальное работает в mock-режиме.

### 3. Запуск демо
python examples/demo.py
Через 2 минуты в папке `output/` появится готовый `.mp4` файл!```
```

## 🤖 Архитектура системы

### Агенты

|Агент|Роль|Вход|Выход|
|---|---|---|---|
|**TrendAnalyst**|Анализирует нишу|Название ниши|JSON с трендами, конкурентами, потенциалом|
|💡 **IdeaGenerator**|Генерирует 10 идей|Анализ ниши|10 идей с viral score (1-10)|
|📝 **ScriptWriter**|Пишет сценарий|Лучшая идея|6 сцен с текстом и визуальным описанием|
|🎨 **VisualDirector**|Создаёт промпты|Сценарий|Промпты для Midjourney/Leonardo/DALL-E|
|🖼️ **ImageGenerator**|Генерирует картинки|Визуальные промпты|6 PNG 1080×1920|
|🎙️ **VoiceArtist**|Озвучивает текст|Сценарий|MP3 файлы с голосом|
|**MusicComposer**|Создаёт музыку|Длительность ролика|Ambient WAV фон|
|🎞️ **VideoEditor**|Монтирует видео|Все ассеты|Готовый MP4 с субтитрами|
### Оркестратор

`Orchestrator` управляет потоком данных между агентами, собирает результаты и сохраняет их в структурированном виде.

---

## 📁 Структура проекта
youtube-shorts-factory/
├── src/
│   ├── agents/
│   │   ├── base_agent.py           # Базовый класс агента
│   │   ├── trend_analyst.py        # 🔍 Анализ ниши
│   │   ├── idea_generator.py       # 💡 Генерация идей
│   │   ├── script_writer.py        # 📝 Сценарий
│   │   ├── visual_director.py      # 🎨 Визуальные промпты
│   │   ├── image_generator.py      # 🖼️ Картинки
│   │   ├── voice_artist.py         # ️ Озвучка
│   │   ├── music_composer.py       # 🎵 Музыка
│   │   └── video_editor.py         # 🎞️ Монтаж
│   ├── orchestrator.py             # 🎯 Главный оркестратор
│   ├── llm_client.py               # 🤖 Клиент DeepSeek API
│   └── config.py                   # ⚙️ Настройки
├── examples/
│   └── demo.py                     # 🚀 Демо-запуск
├── output/                         # 📁 Результаты
├── requirements.txt
├── .env.example
└── README.md

## Конфигурация

### Обязательные API ключи

|API|Зачем|Цена|Получить|
|---|---|---|---|
|**DeepSeek**|Генерация идей, сценариев, промптов|~$0.10 за ролик|[platform.deepseek.com](https://platform.deepseek.com/)|

### Опциональные API (для реального контента)

|API|Зачем|Цена|Получить|
|---|---|---|---|
|**Leonardo AI**|Генерация картинок|~$0.05 за ролик|[leonardo.ai](https://leonardo.ai/)|
|**ElevenLabs**|Озвучка сценария|~$0.10 за ролик|[elevenlabs.io](https://elevenlabs.io/)|
|**YouTube Data API**|Автопубликация|Бесплатно (10K запросов/день)|[Google Cloud Console](https://console.cloud.google.com/)|

Без опциональных ключей система работает в **mock-режиме**: создаёт placeholder-картинки через Pillow и текстовые файлы вместо аудио.

## 🎯 Примеры использования

### 1. Базовый запуск (mock-режим)

```
```bash

python examples/demo.py
```

### 2. С реальным DeepSeek API

```
bash
# В .env добавь: DEEPSEEK_API_KEY=sk-...
python examples/demo.py
```

### 3. Свой сценарий (Python API)

```
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()

result = orchestrator.create_short(
    niche="lifehacks",
    auto_select=True  # Автовыбор лучшей идеи
)

orchestrator.print_summary(result)
```

### 4. Ручной выбор идеи

```
result = orchestrator.create_short(
    niche="rare_facts",
    selected_idea_id=3,  # Конкретная идея
    auto_select=False
)
```

## 📊 Результаты
```

После запуска в `output/{niche}/idea_{id}/` создаётся:
output/rare_facts/idea_01/
├── short_final.mp4              # 🎬 Готовое видео 1080×1920
├── idea_01_the_brain_paradox_...json  #  Полный результат
├── images/                      # 🖼️ 6 сцен (1080×1920)
│   ├── scene_01.png
│   ├── scene_01_subtitled.png   # С субтитрами
│   └── ...
── audio/                       # 🎙️ Тексты озвучки
│   ├── scene_01_voiceover.txt
│   └── full_script.txt
└── music/                       #  Фоновая музыка
    └── background_music.wav
```

Каталог всех идей ведётся в `output/catalog.csv` — удобно отслеживать производство.

## 🛠️ Технологии

- **Python 3.13 — основной язык
- **DeepSeek API** — LLM для генерации контента
- **MoviePy 2.3 — монтаж видео
- **Pillow** — рендеринг субтитров на картинках
- **Requests** — HTTP-клиент для API
- **python-dotenv** — управление секретами

---

## ️ Roadmap

### ✅ Реализовано

- Multi-agent архитектура (7 агентов)
- Mock-режим для тестирования без API
- Генерация сценариев с субтитрами
- Автоматический монтаж видео
- Фоновая музыка (ambient)
- Умная система сохранения результатов
- Каталог всех сгенерированных идей

### В разработке

- Интеграция с Leonardo AI (реальные картинки)
- Интеграция с ElevenLabs (реальная озвучка)
- YouTube Publisher (автозагрузка)
- Поддержка других ниш из коробки
- Веб-интерфейс (Streamlit)

### 💡 Идеи на будущее

- Telegram-бот для управления фабрикой
- Batch-режим (10 роликов за ночь)
- A/B тестирование идей
- Аналитика просмотров после публикации

---

## 🤝 Контрибьют

Приветствуются:

- Новые агенты (например, **SEO-оптимизатор** для тегов)
- Интеграции с другими AI-сервисами
- Улучшения монтажа (переходы, эффекты)
- Документация и переводы

---

## Лицензия

MIT License — используй как хочешь, включая коммерческие проекты.

---

## 👤 Автор
arseniizh.work@yandex.ru
Создано с ❤️ в рамках изучения multi-agent систем и AI-автоматизации контента.

---

## Похожие проекты

- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) — автономные AI-агенты
- [LangChain](https://github.com/langchain-ai/langchain) — фреймворк для LLM-приложений
- [MoviePy](https://github.com/Zulko/moviepy) — монтаж видео на Python
