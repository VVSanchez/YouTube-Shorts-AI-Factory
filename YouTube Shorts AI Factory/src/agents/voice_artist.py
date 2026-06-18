"""
Агент-диктор.
Озвучивает текст сценария.

Два режима:
- Mock: сохраняет текст в .txt файлы (бесплатно)
- Real: генерирует голос через ElevenLabs API
"""

import os
import requests
from typing import Dict, List
from .base_agent import BaseAgent


class VoiceArtist(BaseAgent):
    """Озвучивает сценарий ролика."""
    
    def __init__(self, use_mock: bool = True, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Args:
            use_mock: Если True — сохраняет текст в файлы (без озвучки)
                     Если False — использует ElevenLabs API
            voice_id: ID голоса в ElevenLabs
                     По умолчанию: Rachel (женский, спокойный)
                     Другие: 
                     - "AZnzlk1XvdvUeBnXmlld" (Domi)
                     - "EXAVITQu4vr4xnSDxMaL" (Bella)
                     - "ErXwobaYiN019PkySvjV" (Antoni - мужской)
        """
        system_prompt = "Ты — профессиональный диктор."
        super().__init__(name="VoiceArtist", system_prompt=system_prompt)
        
        self.use_mock = use_mock
        self.voice_id = voice_id
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
        
        if not use_mock and not self.elevenlabs_api_key:
            print("⚠️ ELEVENLABS_API_KEY не найден, переключаюсь в mock-режим")
            self.use_mock = True
    
    def process(self, script: Dict, output_dir: str = "output", **kwargs) -> Dict:
        """
        Озвучивает все сцены сценария.
        
        Args:
            script: Сценарий от ScriptWriter (содержит scenes с voiceover)
            output_dir: Базовая папка для сохранения
        
        Returns:
            Dict с путями к аудиофайлам
        """
        print(f"\n{'='*60}")
        print(f"🎙️  [VoiceArtist] Озвучиваю сценарий...")
        print(f"{'='*60}")
        
        scenes = script.get("scenes", [])
        if not scenes:
            print("⚠️ Нет сцен для озвучки!")
            return {"audio": [], "mode": "mock" if self.use_mock else "real"}
        
        # Создаём папку для аудио
        audio_dir = os.path.join(output_dir, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        
        audio_paths = []
        
        if self.use_mock:
            print("🎭 [MOCK] Сохраняю текст сцен в .txt файлы...")
            audio_paths = self._save_text_files(scenes, audio_dir)
        else:
            print("🎤 [REAL] Генерирую голос через ElevenLabs...")
            audio_paths = self._generate_with_elevenlabs(scenes, audio_dir)
        
        print(f"\n✅ [VoiceArtist] Сгенерировано {len(audio_paths)} аудиофайлов:")
        for path in audio_paths:
            print(f"   🎵 {path}")
        
        return {
            "script": script,
            "audio": audio_paths,
            "mode": "mock" if self.use_mock else "real",
            "audio_dir": audio_dir
        }
    
    def _save_text_files(self, scenes: List[Dict], output_dir: str) -> List[str]:
        """
        Сохраняет текст каждой сцены в отдельный .txt файл.
        Mock-режим для тестирования.
        """
        file_paths = []
        
        for scene in scenes:
            scene_id = scene.get("scene_id", 1)
            voiceover = scene.get("voiceover", "")
            
            # Создаём файл с текстом
            filename = f"scene_{scene_id:02d}_voiceover.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"SCENE {scene_id}\n")
                f.write("="*40 + "\n\n")
                f.write(f"Text to voiceover:\n")
                f.write(f"{voiceover}\n\n")
                f.write(f"Duration: {scene.get('duration', 5)}s\n")
                f.write(f"Emotion: {scene.get('emotion', 'neutral')}\n")
            
            file_paths.append(filepath)
            
            print(f"   📄 Сцена {scene_id}: {voiceover[:50]}...")
        
        # Создаём общий файл со всем текстом
        full_script_path = os.path.join(output_dir, "full_script.txt")
        with open(full_script_path, "w", encoding="utf-8") as f:
            f.write("FULL SCRIPT FOR YOUTUBE SHORT\n")
            f.write("="*60 + "\n\n")
            
            for scene in scenes:
                f.write(f"Scene {scene.get('scene_id')}: {scene.get('voiceover')}\n")
            
            f.write(f"\n{'='*60}\n")
            f.write(f"Total duration: {sum(s.get('duration', 5) for s in scenes)}s\n")
        
        file_paths.append(full_script_path)
        print(f"   📄 Полный скрипт: {full_script_path}")
        
        return file_paths
    
    def _generate_with_elevenlabs(self, scenes: List[Dict], output_dir: str) -> List[str]:
        """
        Генерирует аудио через ElevenLabs API.
        
        ElevenLabs API:
        POST /v1/text-to-speech/{voice_id}
        """
        audio_paths = []
        
        for scene in scenes:
            scene_id = scene.get("scene_id", 1)
            text = scene.get("voiceover", "")
            
            print(f"\n   🎤 Озвучиваю сцену {scene_id}...")
            print(f"      📝 Текст: {text[:60]}...")
            
            try:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": self.elevenlabs_api_key
                }
                
                payload = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5
                    }
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=60)
                
                if response.status_code == 200:
                    filename = f"scene_{scene_id:02d}_voiceover.mp3"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    audio_paths.append(filepath)
                    print(f"      ✅ Сохранено: {filepath}")
                else:
                    print(f"      ❌ Ошибка: HTTP {response.status_code}")
                    print(f"      {response.text[:200]}")
            
            except Exception as e:
                print(f"      💥 Исключение: {e}")
        
        return audio_paths