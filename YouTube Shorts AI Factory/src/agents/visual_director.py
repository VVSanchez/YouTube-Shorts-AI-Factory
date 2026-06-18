"""
Агент-визуальный директор.
Создаёт промпты для генерации изображений.
"""

import json
from typing import Dict
from .base_agent import BaseAgent


class VisualDirector(BaseAgent):
    """Создаёт промпты для генерации визуала."""
    
    def __init__(self):
        system_prompt = """Ты — визуальный директор YouTube Shorts.
Ты создаёшь промпты для AI-генераторов изображений (Midjourney, Leonardo AI, DALL-E).

Твои промпты должны:
- Быть на английском языке
- Содержать: объект, стиль, освещение, композицию, качество
- Подходить для вертикального формата (9:16)
- Создавать единый визуальный стиль across all scenes

Отвечай СТРОГО в JSON формате:
{
    "visual_style": "общий стиль (cinematic/realistic/anime/3d)",
    "color_palette": "основные цвета",
    "scene_prompts": [
        {
            "scene_id": 1,
            "prompt": "детальный промпт для генерации изображения на английском",
            "negative_prompt": "чего избегать (blur, low quality, text)",
            "aspect_ratio": "9:16"
        },
        ...
    ]
}

Отвечай ТОЛЬКО JSON."""
        
        super().__init__(name="VisualDirector", system_prompt=system_prompt)
    
    def process(self, script: Dict, **kwargs) -> Dict:
        """Создаёт промпты для каждой сцены."""
        print(f"\n{'='*60}")
        print(f"🎨 [VisualDirector] Создаю визуальные промпты...")
        print(f"{'='*60}")
        
        scenes_text = "\n".join([
            f"Сцена {s.get('scene_id')}: {s.get('visual')}"
            for s in script.get("scenes", [])
        ])
        
        user_message = f"""Создай промпты для генерации изображений для YouTube Shorts.

СТИЛЬ РОЛИКА: {script.get('title')}
СЦЕНЫ:
{scenes_text}

Создай промпт для каждой сцены на английском языке.
Формат: вертикальный (9:16).
Качество: cinematic, highly detailed, 8k."""
        
        response = self._call_llm(user_message, temperature=0.6)
        
        # Парсим JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                visuals = json.loads(response[start:end])
            else:
                visuals = {"raw_response": response}
        except Exception as e:
            print(f"⚠️ Ошибка парсинга: {e}")
            visuals = {"raw_response": response}
        
        prompts = visuals.get("scene_prompts", [])
        print(f"\n✅ [VisualDirector] Промпты готовы:")
        print(f"   🎨 Стиль: {visuals.get('visual_style')}")
        print(f"   🖼️  Промптов: {len(prompts)}")
        
        return {
            "script": script,
            "visuals": visuals,
            "raw_response": response
        }