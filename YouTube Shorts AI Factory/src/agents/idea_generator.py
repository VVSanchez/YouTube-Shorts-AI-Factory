"""
Агент-генератор идей.
Создаёт 10 вирусных идей для Shorts.
"""

import json
from typing import Dict, List
from .base_agent import BaseAgent


class IdeaGenerator(BaseAgent):
    """Генерирует идеи для Shorts с вау-эффектом."""
    
    def __init__(self):
        system_prompt = """Ты — креативный директор YouTube Shorts.
Ты создаёшь идеи, которые становятся вирусными.

Твои идеи должны:
- Иметь неожиданный финал или эффект "вау"
- Зацеплять с первых 3 секунд
- Вызывать эмоции: любопытство → удивление → осознание
- Быть реализуемыми за 30-60 секунд
- Подходить для англоязычной аудитории (если не указано иное)

Отвечай СТРОГО в JSON формате:
{
    "ideas": [
        {
            "id": 1,
            "title": "короткое название",
            "hook": "зацепка на первые 3 секунды",
            "concept": "описание идеи в 2-3 предложениях",
            "wow_factor": "что создаёт вау-эффект",
            "viral_score": 1-10
        },
        ...
    ]
}

Сгенерируй ровно 10 идей. Отвечай ТОЛЬКО JSON."""
        
        super().__init__(name="IdeaGenerator", system_prompt=system_prompt)
    
    def process(self, niche: str, analysis: Dict = None, **kwargs) -> Dict:
        """Генерирует 10 идей для ниши."""
        print(f"\n{'='*60}")
        print(f"💡 [IdeaGenerator] Генерирую идеи для ниши: {niche}")
        print(f"{'='*60}")
        
        # Формируем запрос с учётом анализа
        context = ""
        if analysis:
            trends = analysis.get("top_trends", [])
            if trends:
                context = f"\nАктуальные тренды: {', '.join(trends)}"
        
        user_message = f"""Придумай 10 вирусных идей для YouTube Shorts в нише '{niche}'.
Каждая идея должна иметь неожиданную развязку или вау-эффект.
Хронометраж: 30-60 секунд.
Аудитория: англоязычная.{context}"""
        
        response = self._call_llm(user_message, temperature=0.9)
        
        # Парсим JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                ideas_data = json.loads(response[start:end])
                ideas = ideas_data.get("ideas", [])
            else:
                ideas = []
        except Exception as e:
            print(f"⚠️ Ошибка парсинга: {e}")
            ideas = []
        
        # Сортируем по viral_score
        ideas = sorted(ideas, key=lambda x: x.get("viral_score", 0), reverse=True)
        
        print(f"\n✅ [IdeaGenerator] Сгенерировано {len(ideas)} идей:")
        for idea in ideas[:3]:  # Показываем топ-3
            print(f"   🎯 #{idea.get('id')}: {idea.get('title')} (viral: {idea.get('viral_score')}/10)")
        
        return {
            "niche": niche,
            "ideas": ideas,
            "raw_response": response
        }