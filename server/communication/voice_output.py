"""
Voice Output - Text-to-Speech using gTTS and edge-tts

Converts AI's text responses to speech.
Using modern, lightweight TTS solutions.
"""

import io
import tempfile
from pathlib import Path
from typing import Optional
import asyncio

from gtts import gTTS
import edge_tts
import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)


class VoiceOutput:
    """
    Text-to-Speech using gTTS (Google) and edge-tts (Microsoft).
    
    Generates natural-sounding speech.
    """
    
    def __init__(self):
        """Initialize voice output system."""
        self.tts_engine = settings.TTS_ENGINE  # "gtts" or "edge"
        self.is_initialized = False
        
        # Edge TTS voice (Turkish male)
        self.edge_voice = "tr-TR-AhmetNeural"  # Male Turkish voice
        
        logger.info("voice_output_created", engine=self.tts_engine)
    
    async def initialize(self):
        """Initialize TTS engine."""
        logger.info("initializing_tts", engine=self.tts_engine)
        
        # No heavy model loading needed for gTTS or edge-tts
        # They use cloud APIs
        
        self.is_initialized = True
        logger.info("tts_initialized")
    
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
            bytes: Audio data (MP3 format)
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.debug(
            "synthesizing_speech",
            text_length=len(text),
            emotion=emotion,
            engine=self.tts_engine,
        )
        
        if self.tts_engine == "edge":
            return await self._synthesize_edge(text, language)
        else:
            return await self._synthesize_gtts(text, language)
    
    async def _synthesize_gtts(self, text: str, language: str) -> bytes:
        """Synthesize with Google TTS."""
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Generate speech with gTTS
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(tmp_path)
            
            # Read generated audio
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            logger.info("gtts_synthesis_complete", size_bytes=len(audio_data))
            return audio_data
        
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    async def _synthesize_edge(self, text: str, language: str) -> bytes:
        """Synthesize with Microsoft Edge TTS (higher quality)."""
        # Map language to voice
        voice = self.edge_voice if language == "tr" else "en-US-GuyNeural"
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Generate speech with edge-tts
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(tmp_path)
            
            # Read generated audio
            with open(tmp_path, "rb") as f:
                audio_data = f.read()
            
            logger.info("edge_tts_synthesis_complete", size_bytes=len(audio_data))
            return audio_data
        
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    async def synthesize_with_style(
        self,
        text: str,
        style: str = "neutral",
    ) -> bytes:
        """
        Synthesize with a specific style.
        
        Args:
            text: Text to speak
            style: Style preset
            
        Returns:
            bytes: Audio data
        """
        return await self.synthesize(text, language="tr")
    
    async def close(self):
        """Close TTS engine."""
        # No cleanup needed for gTTS/edge-tts
        logger.info("voice_output_closed")

