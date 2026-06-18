"""
Базовый класс для всех агентов.
"""

from typing import Dict
from src.llm_client import LLMClient


class BaseAgent:
    """Базовый класс агента."""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.llm_client = LLMClient()
    
    def process(self, input_data: str, **kwargs) -> Dict:
        """
        Обрабатывает входные данные.
        ⚠️ Переопределяется в наследниках!
        """
        raise NotImplementedError(f"❌ Агент {self.name} должен реализовать process()")
    
    def _call_llm(self, user_message: str, temperature: float = 0.7) -> str:
        """Вспомогательный метод для вызова LLM."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        print(f"\n🤖 [{self.name}] Запрос к LLM (t={temperature})...")
        response = self.llm_client.chat(messages, temperature=temperature)
        
        return response