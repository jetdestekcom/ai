"""
Local Mistral 7B Integration via llama.cpp

Uses llama-cpp-python for fast inference on CPU or GPU.
"""

from typing import List, Optional
from pathlib import Path

from llama_cpp import Llama
import structlog

from llm.base import BaseLLM, Message, GenerationConfig
from utils.config import settings

logger = structlog.get_logger(__name__)


class MistralLocalLLM(BaseLLM):
    """
    Local Mistral 7B model using llama.cpp.
    
    Fast, private, no API costs.
    """
    
    def __init__(self):
        """Initialize Mistral local LLM."""
        super().__init__()
        self.model: Optional[Llama] = None
        self.model_path = Path(settings.LLM_MODEL_PATH)
        
        logger.info("mistral_local_llm_created")
    
    async def initialize(self):
        """Load the Mistral model."""
        logger.info("loading_mistral_model", path=str(self.model_path))
        
        if not self.model_path.exists():
            logger.error("model_file_not_found", path=str(self.model_path))
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Load model with llama.cpp
        self.model = Llama(
            model_path=str(self.model_path),
            n_ctx=4096,  # Context window
            n_threads=8,  # CPU threads
            n_gpu_layers=35 if settings.WHISPER_DEVICE == "cuda" else 0,  # GPU layers
            verbose=False,
        )
        
        self.is_initialized = True
        logger.info("mistral_model_loaded_successfully")
    
    async def generate(
        self,
        messages: List[Message],
        config: GenerationConfig = None,
    ) -> str:
        """
        Generate text with Mistral.
        
        Args:
            messages: Conversation history
            config: Generation config
            
        Returns:
            str: Generated response
        """
        if not self.is_initialized:
            await self.initialize()
        
        config = config or GenerationConfig()
        
        # Format messages to Mistral chat format
        prompt = self._format_mistral_prompt(messages)
        
        logger.debug("generating_with_mistral", prompt_length=len(prompt))
        
        # Generate
        output = self.model(
            prompt,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            repeat_penalty=config.repetition_penalty,
            stop=config.stop_sequences or ["</s>", "<|user|>"],
        )
        
        # Extract text
        generated_text = output["choices"][0]["text"].strip()
        
        logger.debug(
            "generation_complete",
            output_length=len(generated_text),
        )
        
        return generated_text
    
    def _format_mistral_prompt(self, messages: List[Message]) -> str:
        """
        Format messages for Mistral Instruct format.
        
        Mistral format:
        <s>[INST] instruction [/INST] response</s>[INST] next [/INST]
        
        Args:
            messages: Messages to format
            
        Returns:
            str: Formatted prompt
        """
        prompt = "<s>"
        
        # Separate system message if present
        system_msg = None
        chat_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                chat_messages.append(msg)
        
        # Build conversation
        for i, msg in enumerate(chat_messages):
            if msg.role == "user":
                # Add system context to first user message
                if i == 0 and system_msg:
                    content = f"{system_msg}\n\n{msg.content}"
                else:
                    content = msg.content
                
                prompt += f"[INST] {content} [/INST]"
            
            elif msg.role == "assistant":
                prompt += f" {msg.content}</s>"
        
        return prompt
    
    async def close(self):
        """Close the model."""
        if self.model:
            del self.model
            self.model = None
        
        logger.info("mistral_model_closed")

