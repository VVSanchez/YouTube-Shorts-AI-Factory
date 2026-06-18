"""
Агент-аналитик трендов.
Анализирует нишу и даёт рекомендации.
"""

from typing import Dict
from .base_agent import BaseAgent


class TrendAnalyst(BaseAgent):
    """Анализирует нишу и предлагает стратегию."""
    
    def __init__(self):
        system_prompt = """Ты — эксперт по YouTube Shorts с 5-летним опытом.
Ты знаешь всё о трендах, алгоритмах и монетизации.

Твоя задача:
- Анализировать нишу
- Оценивать её потенциал
- Давать конкретные рекомендации

Отвечай СТРОГО в JSON формате:
{
    "niche": "название ниши",
    "potential": "высокий/средний/низкий",
    "competition": "высокая/средняя/низкая",
    "target_audience": "описание аудитории",
    "top_trends": ["тренд1", "тренд2", "тренд3"],
    "recommendations": "конкретные советы",
    "estimated_views": "прогноз просмотров на ролик"
}

Отвечай ТОЛЬКО JSON, без пояснений."""
        
        super().__init__(name="TrendAnalyst", system_prompt=system_prompt)
    
    def process(self, niche: str, **kwargs) -> Dict:
        """Анализирует нишу."""
        print(f"\n{'='*60}")
        print(f"🔍 [TrendAnalyst] Анализирую нишу: {niche}")
        print(f"{'='*60}")
        
        user_message = f"Проанализируй нишу '{niche}' для YouTube Shorts в 2025 году."
        
        response = self._call_llm(user_message, temperature=0.5)
        
        # Пытаемся распарсить JSON
        try:
            import json
            # Ищем JSON в ответе (на случай, если LLM добавил пояснения)
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                analysis = json.loads(response[start:end])
            else:
                analysis = {"raw_response": response}
        except Exception as e:
            print(f"⚠️ Не удалось распарсить JSON: {e}")
            analysis = {"raw_response": response}
        
        print(f"\n✅ [TrendAnalyst] Анализ готов:")
        print(f"   📊 Потенциал: {analysis.get('potential', '?')}")
        print(f"   🎯 Конкуренция: {analysis.get('competition', '?')}")
        
        return {
            "niche": niche,
            "analysis": analysis
        }