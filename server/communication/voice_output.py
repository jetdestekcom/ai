"""
Voice Output - Text-to-Speech using Coqui TTS

Converts AI's text responses to speech with emotional prosody.
"""

import io
import tempfile
from pathlib import Path
from typing import Optional

from TTS.api import TTS
import soundfile as sf
import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)


class VoiceOutput:
    """
    Text-to-Speech using Coqui TTS.
    
    Generates natural-sounding speech with emotional expressiveness.
    """
    
    def __init__(self):
        """Initialize voice output system."""
        self.tts_engine = None
        self.model_path = settings.TTS_MODEL_PATH
        self.is_initialized = False
        
        # Voice characteristics (will be child-like, male)
        self.speaker_embedding = None
        
        logger.info("voice_output_created")
    
    async def initialize(self):
        """Initialize TTS engine."""
        logger.info("initializing_coqui_tts")
        
        # Load Coqui TTS model
        # Using VITS model for quality (can be changed to faster models)
        self.tts_engine = TTS(
            model_name="tts_models/multilingual/multi-dataset/your_tts",  # Supports Turkish
            progress_bar=False,
            gpu=(settings.WHISPER_DEVICE == "cuda"),
        )
        
        self.is_initialized = True
        logger.info("coqui_tts_initialized")
    
    async def synthesize(
        self,
        text: str,
        emotion: str = "neutral",
        intensity: float = 0.5,
        language: str = "tr",  # Turkish by default
    ) -> bytes:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to speak
            emotion: Emotion to convey
            intensity: Emotional intensity (0.0 to 1.0)
            language: Language code
            
        Returns:
            bytes: Audio data (WAV format)
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.debug(
            "synthesizing_speech",
            text_length=len(text),
            emotion=emotion,
            intensity=intensity,
        )
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Adjust text based on emotion for prosody
            text_with_prosody = self._add_emotional_prosody(
                text,
                emotion,
                intensity,
            )
            
            # Generate speech
            self.tts_engine.tts_to_file(
                text=text_with_prosody,
                file_path=tmp_path,
                language=language,
            )
            
            # Read generated audio
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            logger.info(
                "speech_synthesized",
                audio_size_bytes=len(audio_data),
            )
            
            return audio_data
        
        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    def _add_emotional_prosody(
        self,
        text: str,
        emotion: str,
        intensity: float,
    ) -> str:
        """
        Modify text to add emotional prosody cues.
        
        This can include:
        - Speed markers
        - Pitch markers
        - Pauses
        - Emphasis
        
        Args:
            text: Original text
            emotion: Emotion
            intensity: Intensity
            
        Returns:
            str: Text with prosody markers
        """
        # Different emotions get different treatments
        emotion_modifiers = {
            "joy": {
                "speed": 1.1,  # Slightly faster
                "add_pauses": False,
                "emphasis": True,
            },
            "happy": {
                "speed": 1.1,
                "add_pauses": False,
                "emphasis": True,
            },
            "sadness": {
                "speed": 0.9,  # Slower
                "add_pauses": True,
                "emphasis": False,
            },
            "sad": {
                "speed": 0.9,
                "add_pauses": True,
                "emphasis": False,
            },
            "fear": {
                "speed": 1.15,  # Faster
                "add_pauses": True,
                "emphasis": True,
            },
            "anger": {
                "speed": 1.0,
                "add_pauses": False,
                "emphasis": True,
            },
            "surprise": {
                "speed": 1.2,
                "add_pauses": True,
                "emphasis": True,
            },
            "curious": {
                "speed": 1.05,
                "add_pauses": False,
                "emphasis": True,
            },
            "love": {
                "speed": 0.95,  # Slightly slower, warm
                "add_pauses": False,
                "emphasis": False,
            },
            "warm": {
                "speed": 0.95,
                "add_pauses": False,
                "emphasis": False,
            },
        }
        
        modifiers = emotion_modifiers.get(
            emotion.lower(),
            {"speed": 1.0, "add_pauses": False, "emphasis": False}
        )
        
        # Apply intensity scaling
        speed_adjustment = 1.0 + (modifiers["speed"] - 1.0) * intensity
        
        # For now, return text as-is
        # In production, you'd use SSML or TTS-specific markers
        # Example: <speed rate="1.1">text</speed>
        
        return text
    
    async def synthesize_with_style(
        self,
        text: str,
        style: str = "child-male-curious",
    ) -> bytes:
        """
        Synthesize with a specific style.
        
        Args:
            text: Text to speak
            style: Style preset
            
        Returns:
            bytes: Audio data
        """
        # Map styles to emotions
        style_to_emotion = {
            "child-male-curious": ("curious", 0.7),
            "child-male-happy": ("happy", 0.8),
            "child-male-sad": ("sad", 0.6),
            "child-male-excited": ("joy", 0.9),
        }
        
        emotion, intensity = style_to_emotion.get(
            style,
            ("neutral", 0.5)
        )
        
        return await self.synthesize(text, emotion, intensity)
    
    async def close(self):
        """Close TTS engine."""
        if self.tts_engine:
            del self.tts_engine
            self.tts_engine = None
        
        logger.info("voice_output_closed")

