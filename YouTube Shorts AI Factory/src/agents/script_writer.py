"""
Агент-сценарист.
Пишет детальный сценарий по кадрам.
"""

import json
from typing import Dict
from .base_agent import BaseAgent


class ScriptWriter(BaseAgent):
    """Пишет сценарий ролика по кадрам."""
    
    def __init__(self):
        system_prompt = """Ты — сценарист вирусных YouTube Shorts.
Ты пишешь сценарии, которые удерживают внимание до конца.

Твой сценарий должен:
- Иметь чёткую структуру: зацепка → развитие → кульминация → развязка
- Содержать 5-7 сцен (кадров)
- Каждая сцена: 5-8 секунд
- Текст для озвучки — короткий, энергичный
- Визуальное описание — конкретное, для генерации картинок

Отвечай СТРОГО в JSON формате:
{
    "title": "название ролика",
    "total_duration": 40,
    "scenes": [
        {
            "scene_id": 1,
            "duration": 5,
            "voiceover": "текст для озвучки (1-2 предложения)",
            "visual": "детальное описание визуального ряда",
            "emotion": "какую эмоцию вызывает (curiosity/shock/awe/laugh)",
            "transition": "тип перехода к следующей сцене (cut/fade/zoom)"
        },
        ...
    ],
    "hook": "зацепка для первых 3 секунд",
    "cta": "призыв к действию в конце"
}

Отвечай ТОЛЬКО JSON."""
        
        super().__init__(name="ScriptWriter", system_prompt=system_prompt)
    
    def process(self, idea: Dict, **kwargs) -> Dict:
        """Пишет сценарий для выбранной идеи."""
        print(f"\n{'='*60}")
        print(f"📝 [ScriptWriter] Пишу сценарий для: {idea.get('title')}")
        print(f"{'='*60}")
        
        user_message = f"""Напиши детальный сценарий для YouTube Shorts.

ИДЕЯ:
Название: {idea.get('title')}
Концепция: {idea.get('concept')}
Зацепка: {idea.get('hook')}
Вау-фактор: {idea.get('wow_factor')}

Сценарий должен быть на 40 секунд, 6 сцен.
Язык озвучки: английский (для англоязычной аудитории)."""
        
        response = self._call_llm(user_message, temperature=0.7)
        
        # Парсим JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                script = json.loads(response[start:end])
            else:
                script = {"raw_response": response}
        except Exception as e:
            print(f"⚠️ Ошибка парсинга: {e}")
            script = {"raw_response": response}
        
        scenes = script.get("scenes", [])
        print(f"\n✅ [ScriptWriter] Сценарий готов:")
        print(f"   🎬 Сцен: {len(scenes)}")
        print(f"   ⏱️  Длительность: {script.get('total_duration')}s")
        print(f"   🎣 Hook: {script.get('hook', '')[:60]}...")
        
        return {
            "idea": idea,
            "script": script,
            "raw_response": response
        }