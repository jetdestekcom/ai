"""
Base LLM interface for text generation.

This provides a unified interface for different LLM backends:
- Local: Mistral 7B via llama.cpp
- API: Claude, GPT-4, etc.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Message:
    """A message in a conversation."""
    role: str  # system, user, assistant
    content: str


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    top_k: int = 40
    repetition_penalty: float = 1.1
    stop_sequences: List[str] = None
    
    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = []


class BaseLLM(ABC):
    """
    Base class for LLM implementations.
    
    All LLM backends must implement this interface.
    """
    
    def __init__(self):
        """Initialize the LLM."""
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self):
        """Initialize the LLM (load model, connect to API, etc.)."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        config: GenerationConfig = None,
    ) -> str:
        """
        Generate text based on conversation history.
        
        Args:
            messages: Conversation history
            config: Generation configuration
            
        Returns:
            str: Generated text
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Close/cleanup the LLM."""
        pass
    
    def format_messages_for_prompt(self, messages: List[Message]) -> str:
        """
        Format messages into a single prompt string.
        
        Default implementation for chat models.
        
        Args:
            messages: List of messages
            
        Returns:
            str: Formatted prompt
        """
        prompt_parts = []
        
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"<|system|>\n{msg.content}\n")
            elif msg.role == "user":
                prompt_parts.append(f"<|user|>\n{msg.content}\n")
            elif msg.role == "assistant":
                prompt_parts.append(f"<|assistant|>\n{msg.content}\n")
        
        # Add final assistant prefix to trigger generation
        prompt_parts.append("<|assistant|>\n")
        
        return "".join(prompt_parts)

