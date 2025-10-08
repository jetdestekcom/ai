"""
Voice Input - Speech-to-Text using Whisper

Converts Cihan's voice to text for processing.
"""

import io
import tempfile
from pathlib import Path
from typing import Optional

import whisper
import numpy as np
import soundfile as sf
import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)


class VoiceInput:
    """
    Speech-to-Text using OpenAI Whisper.
    
    Supports multiple languages including Turkish and English.
    """
    
    def __init__(self):
        """Initialize voice input system."""
        self.model = None
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.device = settings.WHISPER_DEVICE
        self.is_initialized = False
        
        logger.info(
            "voice_input_created",
            model_size=self.model_size,
            device=self.device,
        )
    
    async def initialize(self):
        """Load Whisper model."""
        logger.info("loading_whisper_model", size=self.model_size)
        
        # Load model
        self.model = whisper.load_model(
            self.model_size,
            device=self.device,
        )
        
        self.is_initialized = True
        logger.info("whisper_model_loaded")
    
    async def transcribe(
        self,
        audio_data: bytes,
        audio_format: str = "opus",
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio bytes
            audio_format: Format (opus, wav, mp3, etc.)
            language: Language code (tr, en, etc.) or None for auto-detect
            
        Returns:
            str: Transcribed text
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.debug(
            "transcribing_audio",
            format=audio_format,
            size_bytes=len(audio_data),
            language=language or "auto",
        )
        
        # Convert audio to format Whisper can process
        audio_array = await self._process_audio(audio_data, audio_format)
        
        # Transcribe
        result = self.model.transcribe(
            audio_array,
            language=language,
            fp16=(self.device == "cuda"),
        )
        
        text = result["text"].strip()
        detected_lang = result.get("language", "unknown")
        
        logger.info(
            "transcription_complete",
            text_length=len(text),
            detected_language=detected_lang,
        )
        
        return text
    
    async def _process_audio(
        self,
        audio_data: bytes,
        audio_format: str,
    ) -> np.ndarray:
        """
        Process audio bytes into numpy array for Whisper.
        
        Args:
            audio_data: Raw audio bytes
            audio_format: Audio format
            
        Returns:
            np.ndarray: Audio as numpy array (float32, mono, 16kHz)
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        try:
            # Read audio file
            audio, sample_rate = sf.read(tmp_path)
            
            # Convert to mono if stereo
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            
            # Resample to 16kHz if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                import librosa
                audio = librosa.resample(
                    audio,
                    orig_sr=sample_rate,
                    target_sr=16000,
                )
            
            # Ensure float32
            audio = audio.astype(np.float32)
            
            return audio
        
        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    async def transcribe_stream(
        self,
        audio_chunks: list,
        audio_format: str = "opus",
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe streaming audio chunks.
        
        Args:
            audio_chunks: List of audio byte chunks
            audio_format: Audio format
            language: Language code
            
        Returns:
            str: Transcribed text
        """
        # Combine chunks
        full_audio = b"".join(audio_chunks)
        
        # Transcribe as usual
        return await self.transcribe(full_audio, audio_format, language)
    
    async def close(self):
        """Close and cleanup."""
        if self.model:
            del self.model
            self.model = None
        
        logger.info("voice_input_closed")

