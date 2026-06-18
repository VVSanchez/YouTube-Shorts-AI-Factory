"""
Главный оркестратор — управляет всей цепочкой.
"""

from typing import Dict, List
from .agents.trend_analyst import TrendAnalyst
from .agents.idea_generator import IdeaGenerator
from .agents.script_writer import ScriptWriter
from .agents.visual_director import VisualDirector


class Orchestrator:
    """Оркестратор YouTube Shorts Factory."""
    
    def __init__(self):
        self.trend_analyst = TrendAnalyst()
        self.idea_generator = IdeaGenerator()
        self.script_writer = ScriptWriter()
        self.visual_director = VisualDirector()
    
    def create_short(
        self,
        niche: str,
        selected_idea_id: int = None,
        auto_select: bool = True
    ) -> Dict:
        """
        Создаёт Short от идеи до визуальных промптов.
        
        Args:
            niche: Ниша (lifehacks, rare_facts, и т.д.)
            selected_idea_id: ID выбранной идеи (если None — автовыбор)
            auto_select: Автоматически выбирать лучшую идею
        
        Returns:
            Dict с полным результатом
        """
        print("\n" + "="*60)
        print("🎬 YOUTUBE SHORTS FACTORY — ЗАПУСК")
        print("="*60)
        
        result = {"niche": niche, "steps": {}}
        
        # Шаг 1: Анализ ниши
        print("\n📍 ШАГ 1/4: Анализ ниши")
        trend_result = self.trend_analyst.process(niche)
        result["steps"]["trend_analysis"] = trend_result
        
        # Шаг 2: Генерация идей
        print("\n📍 ШАГ 2/4: Генерация идей")
        ideas_result = self.idea_generator.process(
            niche,
            analysis=trend_result.get("analysis")
        )
        result["steps"]["ideas"] = ideas_result
        
        # Шаг 3: Выбор идеи
        ideas = ideas_result.get("ideas", [])
        if not ideas:
            print("❌ Не удалось сгенерировать идеи!")
            return result
        
        if selected_idea_id:
            selected = next((i for i in ideas if i.get("id") == selected_idea_id), ideas[0])
        elif auto_select:
            selected = ideas[0]  # Лучшая по viral_score
            print(f"\n🎯 Автовыбор: идея #{selected.get('id')} — {selected.get('title')}")
        else:
            # Показываем все идеи для ручного выбора
            print("\n📋 Доступные идеи:")
            for idea in ideas:
                print(f"   #{idea.get('id')}: {idea.get('title')} (viral: {idea.get('viral_score')}/10)")
            selected = ideas[0]
        
        result["selected_idea"] = selected
        
        # Шаг 4: Сценарий
        print("\n📍 ШАГ 3/4: Написание сценария")
        script_result = self.script_writer.process(selected)
        result["steps"]["script"] = script_result
        
        # Шаг 5: Визуальные промпты
        print("\n📍 ШАГ 4/4: Создание визуальных промптов")
        visual_result = self.visual_director.process(script_result.get("script", {}))
        result["steps"]["visuals"] = visual_result
        
        print("\n" + "="*60)
        print("✅ YOUTUBE SHORTS FACTORY — ГОТОВО!")
        print("="*60)
        
        return result
    
    def print_summary(self, result: Dict):
        """Выводит красивое резюме."""
        print("\n" + "="*60)
        print("📊 ИТОГОВОЕ РЕЗЮМЕ")
        print("="*60)
        
        idea = result.get("selected_idea", {})
        script = result.get("steps", {}).get("script", {}).get("script", {})
        visuals = result.get("steps", {}).get("visuals", {}).get("visuals", {})
        
        print(f"\n🎬 РОЛИК:")
        print(f"   📌 Название: {script.get('title', idea.get('title'))}")
        print(f"   ⏱️  Длительность: {script.get('total_duration')}s")
        print(f"   🎣 Hook: {script.get('hook', '')[:80]}")
        print(f"   🎯 CTA: {script.get('cta', '')[:80]}")
        
        print(f"\n🎨 ВИЗУАЛ:")
        print(f"   🖌️  Стиль: {visuals.get('visual_style')}")
        print(f"   🎨 Палитра: {visuals.get('color_palette')}")
        
        scenes = script.get("scenes", [])
        print(f"\n🎬 СЦЕНЫ ({len(scenes)}):")
        for scene in scenes:
            print(f"   [{scene.get('scene_id')}] {scene.get('duration')}s — {scene.get('emotion')}")
            print(f"       🎙️  {scene.get('voiceover', '')[:60]}...")
        
        prompts = visuals.get("scene_prompts", [])
        print(f"\n🖼️  ПРОМПТЫ ДЛЯ ГЕНЕРАЦИИ ({len(prompts)}):")
        for prompt in prompts[:2]:  # Показываем первые 2
            print(f"   [{prompt.get('scene_id')}] {prompt.get('prompt', '')[:80]}...")