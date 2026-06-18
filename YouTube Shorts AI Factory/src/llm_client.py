"""
Клиент для работы с DeepSeek API.
Поддерживает mock-режим для тестирования без API ключей.

JS-аналогия:
    class LLMClient {
        constructor(useMock = false) {
            this.useMock = useMock;
            this.apiKey = process.env.DEEPSEEK_API_KEY;
        }
        
        async chat(messages) {
            if (this.useMock) return this._getMockResponse(messages);
            // ... реальный запрос
        }
    }
"""

import os
import json
import requests
from typing import List, Dict
from dotenv import load_dotenv


class LLMClient:
    """Клиент для отправки запросов к LLM."""
    
    def __init__(self, model: str = "deepseek-chat", use_mock: bool = False):
        """
        Конструктор клиента.
        
        Args:
            model: Название модели
            use_mock: Если True — возвращаем заготовленные ответы (без API)
        """
        load_dotenv()
        
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
        
        # Автоопределение mock-режима
        # Если ключ не задан или это заглушка — включаем mock
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.use_mock = use_mock or not self.api_key or self.api_key.startswith("your-")
        
        if self.use_mock:
            print("🎭 [LLMClient] MOCK-режим активирован (без API ключа)")
        else:
            print(f"🔑 [LLMClient] API ключ найден, работаем с {model}")
    
    def _get_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Возвращает реалистичный заготовленный ответ.
        Определяет, какой агент запросил, по системному промпту.
        
        JS-аналогия:
            function getMockResponse(messages) {
                const systemPrompt = messages[0].content;
                if (systemPrompt.includes('планировщик')) return mockPlan;
                if (systemPrompt.includes('исполнитель')) return mockAnswer;
                return 'Mock response';
            }
        """
        system_prompt = messages[0]["content"].lower() if messages else ""
        user_message = messages[1]["content"].lower() if len(messages) > 1 else ""
        
        # 🔍 TrendAnalyst
        if "эксперт по youtube shorts" in system_prompt or "анализируй нишу" in user_message:
            return json.dumps({
                "niche": "rare_facts",
                "potential": "высокий",
                "competition": "средняя",
                "target_audience": "Любопытные люди 18-35 лет, любящие узнавать новое",
                "top_trends": [
                    "Парадоксы времени",
                    "Загадки океана",
                    "Невероятные способности животных"
                ],
                "recommendations": "Делай упор на визуальные метафоры и неожиданные факты в первые 3 секунды",
                "estimated_views": "50K-200K на ролик при хорошем hook"
            }, ensure_ascii=False)
        
        # 💡 IdeaGenerator
        if "креативный директор" in system_prompt or "придумай 10" in user_message:
            return json.dumps({
                "ideas": [
                    {
                        "id": 1,
                        "title": "The Brain Paradox",
                        "hook": "Your brain can predict the future... but only 1 second ahead",
                        "concept": "Показываем, как мозг обрабатывает информацию с задержкой. В конце — неожиданный факт о дежавю.",
                        "wow_factor": "Зритель осознаёт, что всё, что он видит — это прошлое",
                        "viral_score": 9
                    },
                    {
                        "id": 2,
                        "title": "Ocean's Deepest Secret",
                        "hook": "We've explored more of Mars than our own ocean floor",
                        "concept": "Путешествие от поверхности до Марианской впадины. В конце — звук, который записали на глубине 11 км.",
                        "wow_factor": "Реальный звук из самой глубокой точки Земли",
                        "viral_score": 8
                    },
                    {
                        "id": 3,
                        "title": "Time Travel Fact",
                        "hook": "You're a time traveler right now... and you don't even know it",
                        "concept": "Объясняем, как гравитация замедляет время. Твоя голова старше ног на наносекунды.",
                        "wow_factor": "Физический факт, который меняет восприятие реальности",
                        "viral_score": 8
                    },
                    {
                        "id": 4,
                        "title": "Honey Never Spoils",
                        "hook": "Archaeologists found 3000-year-old honey in Egyptian tombs... and it was still edible",
                        "concept": "Почему мёд — единственная еда, которая не портится. Химия + история.",
                        "wow_factor": "Связь древнего Египта и современной кухни",
                        "viral_score": 7
                    },
                    {
                        "id": 5,
                        "title": "Octopus Minds",
                        "hook": "An octopus has 9 brains... and each arm can think for itself",
                        "concept": "Как работает нервная система осьминога. Каждая рука — отдельный 'мозг'.",
                        "wow_factor": "Невероятная биология, похожая на sci-fi",
                        "viral_score": 8
                    },
                    {
                        "id": 6,
                        "title": "Silent Language",
                        "hook": "There's a language with no words... spoken by 15,000 people daily",
                        "concept": "Язык свиста с Канарских островов — заменяет слова звуками.",
                        "wow_factor": "Реальный язык, который существует сегодня",
                        "viral_score": 7
                    },
                    {
                        "id": 7,
                        "title": "Banana DNA",
                        "hook": "You share 50% of your DNA with a banana",
                        "concept": "Почему люди и бананы так похожи на генетическом уровне.",
                        "wow_factor": "Шокирующий факт о нашем родстве с растениями",
                        "viral_score": 6
                    },
                    {
                        "id": 8,
                        "title": "Lightning vs Sun",
                        "hook": "A single lightning bolt is 5x hotter than the surface of the sun",
                        "concept": "Сравнение температур: молния (30,000°C) vs солнце (5,500°C).",
                        "wow_factor": "Визуальное сравнение масштабов",
                        "viral_score": 7
                    },
                    {
                        "id": 9,
                        "title": "Butterfly Memory",
                        "hook": "Butterflies remember being caterpillars... even after metamorphosis",
                        "concept": "Как память сохраняется через полное превращение тела.",
                        "wow_factor": "Разрушение мифа о 'чистом листе' после метаморфозы",
                        "viral_score": 8
                    },
                    {
                        "id": 10,
                        "title": "Space Smell",
                        "hook": "Astronauts say space smells like seared steak and gunpowder",
                        "concept": "Почему космос имеет запах и как его обнаружили.",
                        "wow_factor": "Неожиданный сенсорный факт о вакууме",
                        "viral_score": 7
                    }
                ]
            }, ensure_ascii=False)
        
        # 📝 ScriptWriter
        if "сценарист вирусных" in system_prompt or "напиши детальный сценарий" in user_message:
            return json.dumps({
                "title": "The Brain Paradox",
                "total_duration": 40,
                "hook": "Your brain is living in the past... and you don't even know it",
                "cta": "Follow for more mind-blowing facts!",
                "scenes": [
                    {
                        "scene_id": 1,
                        "duration": 5,
                        "voiceover": "Your brain is living in the past. Right now.",
                        "visual": "Close-up of a human eye, pupil dilating, cinematic lighting",
                        "emotion": "curiosity",
                        "transition": "cut"
                    },
                    {
                        "scene_id": 2,
                        "duration": 7,
                        "voiceover": "It takes 80 milliseconds for your brain to process what you see.",
                        "visual": "Neural network animation, glowing synapses firing",
                        "emotion": "curiosity",
                        "transition": "fade"
                    },
                    {
                        "scene_id": 3,
                        "duration": 8,
                        "voiceover": "That means everything you perceive... already happened.",
                        "visual": "Split screen: reality vs brain's delayed perception",
                        "emotion": "shock",
                        "transition": "zoom"
                    },
                    {
                        "scene_id": 4,
                        "duration": 7,
                        "voiceover": "You're not experiencing the present. You're watching a replay.",
                        "visual": "Person looking at clock, time slowing down effect",
                        "emotion": "awe",
                        "transition": "cut"
                    },
                    {
                        "scene_id": 5,
                        "duration": 8,
                        "voiceover": "And that feeling of deja vu? That's your brain catching up to reality.",
                        "visual": "Abstract visualization of memory and time overlapping",
                        "emotion": "awe",
                        "transition": "fade"
                    },
                    {
                        "scene_id": 6,
                        "duration": 5,
                        "voiceover": "So... when are you actually living? Follow for more.",
                        "visual": "Question mark dissolving into stars, channel logo",
                        "emotion": "curiosity",
                        "transition": "cut"
                    }
                ]
            }, ensure_ascii=False)
        
        # 🎨 VisualDirector
        if "визуальный директор" in system_prompt or "создай промпты" in user_message:
            return json.dumps({
                "visual_style": "cinematic, hyper-realistic, dark moody atmosphere",
                "color_palette": "deep blue, gold accents, black shadows",
                "scene_prompts": [
                    {
                        "scene_id": 1,
                        "prompt": "Extreme close-up of human eye, pupil dilating dramatically, cinematic lighting, hyper-realistic, 8k, vertical 9:16",
                        "negative_prompt": "blur, low quality, text, watermark",
                        "aspect_ratio": "9:16"
                    },
                    {
                        "scene_id": 2,
                        "prompt": "Glowing neural network inside human head, blue and gold synapses firing, dark background, cinematic, 8k, vertical 9:16",
                        "negative_prompt": "cartoon, low quality, text",
                        "aspect_ratio": "9:16"
                    },
                    {
                        "scene_id": 3,
                        "prompt": "Split screen composition, left side reality, right side delayed perception with ghost effect, cinematic, vertical 9:16",
                        "negative_prompt": "blur, text, watermark",
                        "aspect_ratio": "9:16"
                    },
                    {
                        "scene_id": 4,
                        "prompt": "Person looking at vintage clock, time slowing down visual effect, particles in air, moody lighting, vertical 9:16",
                        "negative_prompt": "cartoon, low quality",
                        "aspect_ratio": "9:16"
                    },
                    {
                        "scene_id": 5,
                        "prompt": "Abstract visualization of memory and time overlapping, golden threads in dark space, cinematic, 8k, vertical 9:16",
                        "negative_prompt": "text, watermark, blur",
                        "aspect_ratio": "9:16"
                    },
                    {
                        "scene_id": 6,
                        "prompt": "Large question mark dissolving into stars and galaxies, deep blue space background, cinematic, vertical 9:16",
                        "negative_prompt": "low quality, cartoon",
                        "aspect_ratio": "9:16"
                    }
                ]
            }, ensure_ascii=False)
        
        # Дефолтный ответ
        return "Mock response: no specific handler found for this request."
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Отправляет запрос к LLM и возвращает ответ."""
        
        # 🎭 MOCK-РЕЖИМ
        if self.use_mock:
            print("   🎭 [MOCK] Возвращаю заготовленный ответ...")
            return self._get_mock_response(messages)
        
        # 🔑 РЕАЛЬНЫЙ API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"ERROR: HTTP {response.status_code} - {response.text[:200]}"
        
        except Exception as e:
            return f"ERROR: {str(e)}"