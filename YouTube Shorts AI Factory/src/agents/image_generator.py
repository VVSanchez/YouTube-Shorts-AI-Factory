"""
Агент-генератор изображений.
Создаёт картинки для каждой сцены ролика.

Два режима:
- Mock: создаёт placeholder'ы через Pillow (бесплатно)
- Real: отправляет промпты в Leonardo AI (нужен API ключ)
"""

import os
import time
import requests
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont
from .base_agent import BaseAgent


class ImageGenerator(BaseAgent):
    """Генерирует изображения для сцен ролика."""
    
    def __init__(self, use_mock: bool = True):
        system_prompt = """Ты — AI-генератор изображений."""
        super().__init__(name="ImageGenerator", system_prompt=system_prompt)
        
        self.use_mock = use_mock
        self.leonardo_api_key = os.getenv("LEONARDO_API_KEY", "")
        
        if not use_mock and not self.leonardo_api_key:
            print("⚠️ LEONARDO_API_KEY не найден, переключаюсь в mock-режим")
            self.use_mock = True
    
    def process(self, visuals: Dict, output_dir: str = "output", **kwargs) -> Dict:
        """Генерирует изображения для всех сцен."""
        print(f"\n{'='*60}")
        print(f"🖼️  [ImageGenerator] Генерирую изображения...")
        print(f"{'='*60}")
        
        scene_prompts = visuals.get("scene_prompts", [])
        if not scene_prompts:
            print("⚠️ Нет промптов для генерации!")
            return {"images": [], "mode": "mock" if self.use_mock else "real"}
        
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        if self.use_mock:
            print("🎭 [MOCK] Создаю placeholder'ы через Pillow...")
            image_paths = self._generate_placeholders(scene_prompts, images_dir)
        else:
            print("🎨 [REAL] Отправляю промпты в Leonardo AI...")
            image_paths = self._generate_with_leonardo(scene_prompts, images_dir)
        
        print(f"\n✅ [ImageGenerator] Сгенерировано {len(image_paths)} изображений:")
        for path in image_paths:
            print(f"   📄 {path}")
        
        return {
            "visuals": visuals,
            "images": image_paths,
            "mode": "mock" if self.use_mock else "real",
            "images_dir": images_dir
        }
    
    def _generate_placeholders(self, scene_prompts: List[Dict], output_dir: str) -> List[str]:
        """Создаёт placeholder'ы через Pillow."""
        image_paths = []
        
        colors = [
            (70, 130, 180),
            (65, 105, 225),
            (138, 43, 226),
            (148, 103, 189),
            (123, 104, 238),
            (100, 149, 237),
        ]
        
        for i, scene in enumerate(scene_prompts):
            scene_id = scene.get("scene_id", i + 1)
            prompt_text = scene.get("prompt", "")[:100]
            
            width, height = 1080, 1920
            img = Image.new('RGB', (width, height), color=colors[i % len(colors)])
            draw = ImageDraw.Draw(img)
            
            try:
                font_large = ImageFont.truetype("arial.ttf", 120)
                font_medium = ImageFont.truetype("arial.ttf", 60)
                font_small = ImageFont.truetype("arial.ttf", 40)
            except (IOError, OSError) as font_error:
                print(f"   ⚠️ Шрифт не найден, используем дефолтный: {font_error}")
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            scene_text = f"SCENE {scene_id}"
            bbox = draw.textbbox((0, 0), scene_text, font=font_large)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, 200), scene_text, fill='white', font=font_large)
            
            y_position = 500
            words = prompt_text.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=font_medium)
                if bbox[2] - bbox[0] < width - 100:
                    line = test_line
                else:
                    draw.text((50, y_position), line, fill='white', font=font_medium)
                    y_position += 80
                    line = word
            if line:
                draw.text((50, y_position), line, fill='white', font=font_medium)
            
            draw.text((50, height - 150), "🎭 MOCK MODE", fill='yellow', font=font_small)
            draw.text((50, height - 100), f"Prompt: {prompt_text[:50]}...", fill='white', font=font_small)
            
            filename = f"scene_{scene_id:02d}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath, 'PNG')
            image_paths.append(filepath)
        
        return image_paths
    
    def _generate_with_leonardo(self, scene_prompts: List[Dict], output_dir: str) -> List[str]:
        """Генерирует изображения через Leonardo AI API."""
        image_paths = []
        
        for i, scene in enumerate(scene_prompts):
            scene_id = scene.get("scene_id", i + 1)
            prompt = scene.get("prompt", "")
            negative_prompt = scene.get("negative_prompt", "blur, low quality, text, watermark")
            
            print(f"\n   🎨 Генерирую сцену {scene_id}...")
            print(f"      📝 Prompt: {prompt[:80]}...")
            
            try:
                headers = {
                    "Authorization": f"Bearer {self.leonardo_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": 768,
                    "height": 1344,
                    "num_images": 1,
                    "model_id": "6bef9f1b-295d-4f61-933b-374081a3e7f1",
                    "alchemy": True,
                    "photoReal": True
                }
                
                response = requests.post(
                    "https://cloud.leonardo.ai/api/rest/v1/generations",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code != 200:
                    print(f"      ❌ Ошибка: HTTP {response.status_code}")
                    continue
                
                data = response.json()
                generation_id = data.get("sdGenerationJob", {}).get("generationId")
                
                if not generation_id:
                    print(f"      ❌ Не получен generationId")
                    continue
                
                print(f"      ⏳ Ожидаю генерацию (ID: {generation_id})...")
                
                image_url = None
                for attempt in range(30):
                    time.sleep(5)
                    
                    status_response = requests.get(
                        f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                        headers=headers,
                        timeout=30
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get("status")
                        
                        if status == "COMPLETE":
                            images = status_data.get("generated_images", [])
                            if images:
                                image_url = images[0].get("url")
                            break
                        elif status == "FAILED":
                            print(f"      ❌ Генерация не удалась")
                            break
                
                if not image_url:
                    print(f"      ❌ Не удалось получить изображение")
                    continue
                
                img_response = requests.get(image_url, timeout=60)
                if img_response.status_code == 200:
                    filename = f"scene_{scene_id:02d}.png"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    image_paths.append(filepath)
                    print(f"      ✅ Сохранено: {filepath}")
                else:
                    print(f"      ❌ Ошибка скачивания: HTTP {img_response.status_code}")
            
            except Exception as e:
                print(f"      💥 Исключение: {e}")
        
        return image_paths