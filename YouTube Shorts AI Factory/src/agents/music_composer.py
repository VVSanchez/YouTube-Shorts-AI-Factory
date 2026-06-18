"""
Агент-композитор.
Генерирует фоновую музыку для ролика.

Mock-режим: создаёт ambient WAV через numpy + scipy.
Real-режим: Suno API (в будущем).
"""

import os
import struct
import wave
import math
import random
from typing import Dict
from .base_agent import BaseAgent


class MusicComposer(BaseAgent):
    """Генерирует фоновую музыку."""
    
    def __init__(self, use_mock: bool = True):
        system_prompt = "Ты — музыкальный продюсер."
        super().__init__(name="MusicComposer", system_prompt=system_prompt)
        
        self.use_mock = use_mock
    
    def process(
        self,
        duration: float = 40.0,
        output_dir: str = "output",
        **kwargs
    ) -> Dict:
        """
        Генерирует фоновую музыку заданной длительности.
        
        Args:
            duration: Длительность в секундах
            output_dir: Папка для сохранения
        
        Returns:
            Dict с путём к аудиофайлу
        """
        print(f"\n{'='*60}")
        print(f"🎵 [MusicComposer] Генерирую фоновую музыку...")
        print(f"{'='*60}")
        
        music_dir = os.path.join(output_dir, "music")
        os.makedirs(music_dir, exist_ok=True)
        
        if self.use_mock:
            print("🎭 [MOCK] Создаю ambient WAV через numpy...")
            music_path = self._generate_ambient_wav(duration, music_dir)
        else:
            print("🎹 [REAL] TODO: Suno API")
            music_path = self._generate_ambient_wav(duration, music_dir)
        
        if music_path:
            file_size_kb = os.path.getsize(music_path) / 1024
            print(f"\n✅ [MusicComposer] Музыка готова!")
            print(f"   🎵 Путь: {music_path}")
            print(f"   📏 Размер: {file_size_kb:.1f} KB")
            print(f"   ⏱️  Длительность: {duration}s")
        
        return {
            "music_path": music_path,
            "duration": duration,
            "mode": "mock" if self.use_mock else "real",
            "music_dir": music_dir
        }
    
    def _generate_ambient_wav(self, duration: float, output_dir: str) -> str:
        """
        Генерирует простой ambient WAV файл.
        Использует чистый Python (wave + math) — без numpy/scipy.
        
        Что получится:
        - Мягкий ambient звук (несколько синусоид с разными частотами)
        - Плавное затухание в начале и конце (fade in/out)
        - Тихий, не мешает озвучке
        
        JS-аналогия:
            Это как Web Audio API:
            const oscillator = audioCtx.createOscillator();
            oscillator.frequency.value = 220;
            oscillator.type = 'sine';
        """
        filepath = os.path.join(output_dir, "background_music.wav")
        
        sample_rate = 44100  # CD качество
        num_samples = int(duration * sample_rate)
        
        # Частоты для ambient звука (мягкие, низкие)
        frequencies = [110.0, 164.81, 220.0, 329.63]  # A2, E3, A3, E4
        amplitudes = [0.15, 0.10, 0.08, 0.05]  # Тихие, чтобы не мешали голосу
        
        # Длительность fade in/out в секундах
        fade_duration = 2.0
        fade_samples = int(fade_duration * sample_rate)
        
        # Генерируем семплы
        samples = []
        for i in range(num_samples):
            t = i / sample_rate  # Время в секундах
            
            # Суммируем синусоиды
            value = 0.0
            for freq, amp in zip(frequencies, amplitudes):
                # Добавляем лёгкую расстройку для "живости"
                detune = random.uniform(-0.5, 0.5)
                value += amp * math.sin(2.0 * math.pi * (freq + detune) * t)
            
            # Fade in (первые 2 секунды)
            if i < fade_samples:
                fade_factor = i / fade_samples
                value *= fade_factor
            
            # Fade out (последние 2 секунды)
            elif i > num_samples - fade_samples:
                fade_factor = (num_samples - i) / fade_samples
                value *= fade_factor
            
            # Ограничиваем диапазон [-1.0, 1.0]
            value = max(-1.0, min(1.0, value))
            
            # Конвертируем в 16-bit integer
            sample_int = int(value * 32767)
            samples.append(sample_int)
        
        # Записываем WAV файл
        try:
            with wave.open(filepath, 'w') as wav_file:
                wav_file.setnchannels(1)       # Моно
                wav_file.setsampwidth(2)        # 16-bit
                wav_file.setframerate(sample_rate)  # 44100 Hz
                
                # Конвертируем семплы в байты
                raw_data = struct.pack(f'<{len(samples)}h', *samples)
                wav_file.writeframes(raw_data)
            
            return filepath
        
        except Exception as e:
            print(f"❌ Ошибка создания WAV: {e}")
            return None