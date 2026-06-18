"""
Конфигурация проекта.
JS-аналогия: это как config.js с настройками.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Загружаем .env
load_dotenv()


# === ПУТИ ===
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Создаём папки
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)


# === API КЛЮЧИ ===
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")


# === НАСТРОЙКИ ВИДЕО ===
VIDEO_CONFIG = {
    "width": 1080,           # Ширина (вертикальное видео)
    "height": 1920,          # Высота
    "fps": 30,               # Кадры в секунду
    "duration": 40,          # Длительность в секундах
    "scenes_count": 6,       # Количество сцен
}


# === НАСТРОЙКИ LLM ===
LLM_CONFIG = {
    "model": "deepseek-chat",
    "temperature_idea": 0.9,      # Высокая для креатива (идеи)
    "temperature_script": 0.7,    # Средняя для сценария
    "temperature_visual": 0.6,    # Ниже для чётких промптов
    "max_tokens": 2000,
}


# === НИШИ (популярные в 2025) ===
NICHES = [
    "lifehacks",           # Лайфхаки
    "rare_facts",          # Редкие факты
    "science_explained",   # Простое объяснение сложного
    "ai_art",              # AI-арт
    "mini_stories",        # Мини-истории с развязкой
    "psychology",          # Психология
    "finance_tips",        # Финансовые советы
    "tech_reviews",        # Обзоры технологий
]