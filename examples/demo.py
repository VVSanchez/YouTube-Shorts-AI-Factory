"""
Демонстрационный запуск YouTube Shorts Factory.
Сохраняет результаты с умной системой именования.
"""

import sys
import os
import json
import re
import csv
from datetime import datetime
from typing import Dict, Tuple

# Добавляем корень проекта в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import Orchestrator
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """
    Кастомный JSON encoder, который умеет работать с NumPy типами.
    
    Проблема: json.dump() не знает, как сериализовать numpy.int64, numpy.float64
    Решение: конвертируем их в обычные Python типы
    
    JS-аналогия:
        JSON.stringify(obj, (key, value) => {
            if (typeof value === 'bigint') return value.toString();
            return value;
        });
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def sanitize_filename(name: str, max_length: int = 30) -> str:
    """
    Превращает строку в безопасное имя файла.
    
    JS-аналогия:
        function sanitizeFilename(name) {
            return name
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, '_')  // только буквы/цифры/подчёркивания
                .replace(/^_+|_+$/g, '')       // убираем подчёркивания по краям
                .substring(0, 30);             // ограничиваем длину
        }
    
    Примеры:
        "The Brain Paradox" → "the_brain_paradox"
        "Ocean's Deepest Secret" → "oceans_deepest_secret"
        "Как это работает?!" → "kak_eto_rabotaet"
    """
    # Приводим к нижнему регистру
    name = name.lower()
    
    # Заменяем всё, кроме букв/цифр, на подчёркивания
    name = re.sub(r'[^a-z0-9а-я]+', '_', name)
    
    # Убираем подчёркивания по краям
    name = name.strip('_')
    
    # Ограничиваем длину
    if len(name) > max_length:
        name = name[:max_length].rstrip('_')
    
    # Если имя пустое (например, только спецсимволы) — даём дефолтное
    if not name:
        name = "untitled"
    
    return name


def save_result(result: Dict, output_base: str = "output") -> Tuple[str, str]:
    """
    Сохраняет результат с умным именем файла.
    """
    niche = result.get("niche", "unknown")
    idea = result.get("selected_idea", {})
    idea_id = idea.get("id", 0)
    idea_title = idea.get("title", "untitled")
    viral_score = idea.get("viral_score", 0)
    
    # 1. Создаём подпапку для ниши
    niche_dir = os.path.join(output_base, sanitize_filename(niche))
    os.makedirs(niche_dir, exist_ok=True)
    
    # 2. Формируем имя файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = sanitize_filename(idea_title)
    filename = f"idea_{idea_id:02d}_{safe_title}_{timestamp}.json"
    filepath = os.path.join(niche_dir, filename)
    
    # 3. Сохраняем JSON с кастомным encoder (для NumPy типов)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
    
    # 4. Добавляем запись в каталог (catalog.csv)
    catalog_path = os.path.join(output_base, "catalog.csv")
    file_exists = os.path.exists(catalog_path)
    
    # Извлекаем нужные данные для каталога
    script = result.get("steps", {}).get("script", {}).get("script", {})
    visuals = result.get("steps", {}).get("visuals", {}).get("visuals", {})
    
    catalog_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "niche": niche,
        "idea_id": int(idea_id),  # Принудительно конвертируем в обычный int
        "title": idea_title,
        "hook": idea.get("hook", ""),
        "viral_score": int(viral_score) if viral_score else 0,  # То же самое
        "total_duration": int(script.get("total_duration", 0)),
        "scenes_count": len(script.get("scenes", [])),
        "visual_style": visuals.get("visual_style", ""),
        "filepath": filepath,
    }
    
    # Записываем в CSV (с заголовками, если файл новый)
    with open(catalog_path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=catalog_entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(catalog_entry)
    
    return filepath, catalog_path


def main():
    """Демонстрация работы фабрики."""
    print("\n" + "="*60)
    print("🎬 YouTube Shorts Factory — Demo")
    print("="*60)
    
    # Создаём оркестратор
    orchestrator = Orchestrator()
    
    # Выбираем нишу
    niche = "rare_facts"
    
    print(f"\n🎯 Ниша: {niche}")
    print("🚀 Запускаем фабрику...\n")
    
    # Создаём Short (шаги 1-4: анализ, идеи, сценарий, визуальные промпты)
    result = orchestrator.create_short(
        niche=niche,
        auto_select=True
    )
    
    # 🔥 ШАГ 5: Генерация изображений
    print("\n📍 ШАГ 5/8: Генерация изображений")
    
    from src.agents.image_generator import ImageGenerator
    
    # Создаём папку для этой идеи
    idea = result.get("selected_idea", {})
    idea_id = idea.get("id", 1)
    output_dir = os.path.join("output", sanitize_filename(niche), f"idea_{idea_id:02d}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Генерируем картинки
    image_gen = ImageGenerator(use_mock=True)
    visuals = result.get("steps", {}).get("visuals", {}).get("visuals", {})
    images_result = image_gen.process(visuals, output_dir=output_dir)
    
    result["steps"]["images"] = images_result

    #  ШАГ 6: Озвучка сценария
    print("\n📍 ШАГ 6/8: Озвучка сценария")
    
    from src.agents.voice_artist import VoiceArtist
    
    script = result.get("steps", {}).get("script", {}).get("script", {})
    voice_artist = VoiceArtist(use_mock=True)
    voice_result = voice_artist.process(script, output_dir=output_dir)
    
    result["steps"]["voice"] = voice_result
    
    print(f"   🎙️  Аудио: {voice_result.get('audio_dir')}")

    # 🔥 ШАГ 7: Генерация фоновой музыки
    print("\n📍 ШАГ 7/8: Генерация фоновой музыки")
    
    from src.agents.music_composer import MusicComposer
    
    total_duration = script.get("total_duration", 40)
    composer = MusicComposer(use_mock=True)
    music_result = composer.process(
        duration=float(total_duration),
        output_dir=output_dir
    )
    
    result["steps"]["music"] = music_result
    
    print(f"    Музыка: {music_result.get('music_path')}")

    # 🔥 ШАГ 8: Сборка финального видео
    print("\n ШАГ 8/8: Сборка финального видео")
    
    from src.agents.video_editor import VideoEditor
    
    video_editor = VideoEditor()
    video_result = video_editor.process(
        script=script,
        images_dir=images_result.get("images_dir"),
        audio_dir=voice_result.get("audio_dir"),
        output_path=os.path.join(output_dir, "short_final.mp4"),
        music_path=music_result.get("music_path") 
    )
    
    result["steps"]["video"] = video_result
    
    if video_result.get("video_path"):
        print(f"   ️  Видео: {video_result.get('video_path')}")
        print(f"   ⏱️  Длительность: {video_result.get('duration', 0):.1f}s")
    
    # Выводим резюме
    orchestrator.print_summary(result)
    
    # 🔥 УМНОЕ СОХРАНЕНИЕ
    filepath, catalog_path = save_result(result)
    
    print(f"\n💾 Результат сохранён:")
    print(f"   📄 JSON: {filepath}")
    print(f"   📚 Каталог: {catalog_path}")
    print(f"   🖼️  Картинки: {images_result.get('images_dir')}")
    
    print("\n" + "="*60)
    print("✅ Demo завершена!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()