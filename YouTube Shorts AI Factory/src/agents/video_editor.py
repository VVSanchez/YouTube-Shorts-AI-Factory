"""
Агент-монтажёр.
Собирает финальное видео из картинок и сценария.

Обновлено для MoviePy 2.x (актуальная версия).
"""

import os
from typing import Dict, List
from PIL import Image, ImageDraw, ImageFont

# MoviePy 2.x — импорты напрямую из moviepy
from moviepy import (
    ImageClip,
    concatenate_videoclips,
)

from .base_agent import BaseAgent


class VideoEditor(BaseAgent):
    """Собирает финальное видео из ассетов."""
    
    def __init__(self):
        system_prompt = "Ты — профессиональный видеомонтажёр."
        super().__init__(name="VideoEditor", system_prompt=system_prompt)
    
    def process(
        self,
        script: Dict,
        images_dir: str,
        audio_dir: str = None,
        output_path: str = "output/short_final.mp4",
        music_path: str = None,
        **kwargs
    ) -> Dict:
        """Собирает финальное видео."""
        print(f"\n{'='*60}")
        print(f"🎞️  [VideoEditor] Собираю видео...")
        print(f"{'='*60}")
        
        scenes = script.get("scenes", [])
        if not scenes:
            print("⚠️ Нет сцен для монтажа!")
            return {"video_path": None}
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Шаг 1: Субтитры
        print("\n📸 Шаг 1: Рендерю субтитры на картинках...")
        frames_with_subtitles = self._render_subtitles(scenes, images_dir)
        
        if not frames_with_subtitles:
            print(" Не удалось подготовить кадры!")
            return {"video_path": None}
        
        # Шаг 2: Клипы
        print("\n🎬 Шаг 2: Создаю видеоклипы...")
        clips = self._create_clips(frames_with_subtitles, scenes)
        
        if not clips:
            print("❌ Не удалось создать клипы!")
            return {"video_path": None}
        
        # Шаг 3: Переходы
        print("\n✨ Шаг 3: Добавляю переходы...")
        clips_with_transitions = self._add_transitions(clips)
        
        # Шаг 4: Склеиваем
        print("\n Шаг 4: Склеиваю в единое видео...")
        final_clip = concatenate_videoclips(clips_with_transitions, method="compose")
        
        # Шаг 5: 🔥 ДОБАВЛЯЕМ МУЗЫКУ
        print(f"\n🎵 Шаг 5: Проверяю музыку...")
        print(f"   music_path = {music_path}")
        
        has_audio = False
        
        if music_path and os.path.exists(music_path):
            print(f"   ✅ Файл музыки найден!")
            try:
                from moviepy import AudioFileClip, CompositeAudioClip
                
                music_clip = AudioFileClip(music_path)
                print(f"    Музыка: {music_clip.duration}s, {music_clip.fps}Hz")
                
                # Обрезаем музыку до длительности видео
                if music_clip.duration > final_clip.duration:
                    music_clip = music_clip.subclipped(0, final_clip.duration)
                    print(f"   ✂️  Обрезана до {music_clip.duration}s")
                
                # Уменьшаем громкость
                music_clip = music_clip.with_volume_scaled(0.3)
                print(f"   🔊 Громкость: 30%")
                
                # Накладываем на видео
                final_clip = final_clip.with_audio(music_clip)
                has_audio = True
                print(f"   ✅ Музыка добавлена в видео!")
                
            except Exception as e:
                print(f"   ❌ Ошибка добавления музыки: {e}")
                import traceback
                traceback.print_exc()
                has_audio = False
        else:
            print(f"   ⚠️ Музыка не найдена (music_path={music_path})")
        
        # Шаг 6: Экспорт
        print(f"\n💾 Шаг 6: Экспортирую в {output_path}...")
        print(f"   audio={has_audio}")
        print(f"   ⏳ Это может занять 30-60 секунд...")
        
        try:
            final_clip.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio=has_audio,  # ← ВАЖНО: True только если есть музыка
                audio_codec="aac" if has_audio else None,
                logger=None
            )
            
            duration = final_clip.duration
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            
            for clip in clips:
                clip.close()
            final_clip.close()
            
            print(f"\n✅ [VideoEditor] Видео готово!")
            print(f"   📁 Путь: {output_path}")
            print(f"   📏 Размер: {file_size_mb:.2f} MB")
            print(f"   ⏱️  Длительность: {duration:.1f}s")
            print(f"   🔊 Звук: {'✅ есть' if has_audio else '❌ нет'}")
            
            return {
                "video_path": output_path,
                "duration": duration,
                "size_mb": file_size_mb,
                "scenes_count": len(scenes),
                "has_audio": has_audio
            }
        
        except Exception as e:
            print(f"\n❌ Ошибка экспорта: {e}")
            import traceback
            traceback.print_exc()
            return {"video_path": None, "error": str(e)}
    
    def _render_subtitles(
        self,
        scenes: List[Dict],
        images_dir: str
    ) -> List[str]:
        """Рендерит субтитры прямо на картинках через Pillow."""
        frames_with_subs = []
        
        for scene in scenes:
            scene_id = scene.get("scene_id", 1)
            voiceover = scene.get("voiceover", "")
            
            # Ищем исходную картинку
            source_path = os.path.join(images_dir, f"scene_{scene_id:02d}.png")
            if not os.path.exists(source_path):
                print(f"   ⚠️ Картинка не найдена: {source_path}")
                continue
            
            # Открываем картинку и конвертируем в RGBA (для прозрачности)
            img = Image.open(source_path).convert("RGBA")
            width, height = img.size
            
            # Загружаем шрифт для субтитров
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except (IOError, OSError):
                font = ImageFont.load_default()
            
            # 🔥 ИСПРАВЛЕНИЕ: создаём overlay РАЗМЕРОМ С ОСНОВНОЕ ИЗОБРАЖЕНИЕ
            # (а не 400px высотой)
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Прозрачный фон
            
            # Разбиваем текст на строки
            lines = self._wrap_text(voiceover, font, width - 100, ImageDraw.Draw(overlay))
            
            # Рисуем текст на overlay (в нижней части кадра)
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Вычисляем позицию: начинаем за 350px от низа
            y_offset = height - 350
            
            # Рисуем полупрозрачный фон под текст
            text_height = len(lines) * 80 + 40
            bg_rect = Image.new('RGBA', (width, text_height), (0, 0, 0, 180))
            overlay.paste(bg_rect, (0, y_offset - 20))
            
            # Рисуем сам текст
            for line in lines:
                # Тень для читаемости
                overlay_draw.text((52, y_offset + 2), line, font=font, fill='black')
                # Основной текст
                overlay_draw.text((50, y_offset), line, font=font, fill='white')
                y_offset += 80
            
            # Накладываем overlay на картинку (теперь размеры совпадают!)
            img = Image.alpha_composite(img, overlay)
            
            # Сохраняем результат
            output_path = os.path.join(images_dir, f"scene_{scene_id:02d}_subtitled.png")
            img.convert('RGB').save(output_path, 'PNG')
            frames_with_subs.append(output_path)
            
            print(f"   ✅ Сцена {scene_id}: субтитры нанесены")
        
        return frames_with_subs
    
    def _wrap_text(
        self,
        text: str,
        font: ImageFont.ImageFont,
        max_width: int,
        draw: ImageDraw.Draw
    ) -> List[str]:
        """Разбивает текст на строки, чтобы они влезали в заданную ширину."""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _create_clips(
        self,
        frames_with_subs: List[str],
        scenes: List[Dict]
    ):
        """Создаёт видеоклипы из картинок с заданной длительностью."""
        clips = []
        
        for i, frame_path in enumerate(frames_with_subs):
            if i >= len(scenes):
                break
            
            duration = scenes[i].get("duration", 5)
            
            # MoviePy 2.x — ImageClip создаётся так же
            clip = ImageClip(frame_path, duration=duration)
            # MoviePy 2.x — resized вместо resize
            clip = clip.resized((1080, 1920))
            
            clips.append(clip)
            print(f"   🎬 Клип {i+1}: {duration}s")
        
        return clips
    
    def _add_transitions(self, clips) -> List:
        """Добавляет плавные переходы (fade in/out) между клипами."""
        from moviepy import vfx
        
        transitioned = []
        
        for i, clip in enumerate(clips):
            if i == 0:
                clip = clip.with_effects([vfx.FadeIn(0.5)])
            elif i == len(clips) - 1:
                clip = clip.with_effects([vfx.FadeOut(0.5)])
            else:
                clip = clip.with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.3)])
            
            transitioned.append(clip)
        
        return transitioned