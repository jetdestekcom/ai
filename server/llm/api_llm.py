"""
API-based LLM (Claude, GPT-4, etc.)

Fallback for when local model isn't sufficient or for complex reasoning.
"""

from typing import List, Optional
import anthropic
import openai
import asyncio

import structlog

from llm.base import BaseLLM, Message, GenerationConfig
from llm.simple_llm import SimpleLLM
from utils.config import settings

logger = structlog.get_logger(__name__)


class APILLM(BaseLLM):
    """
    API-based LLM using Claude or GPT-4.
    
    Higher quality but costs money and requires internet.
    """
    
    def __init__(self):
        """Initialize API LLM."""
        super().__init__()
        self.provider = settings.LLM_API_PROVIDER  # "claude" or "openai"
        self.api_key = settings.LLM_API_KEY
        
        self.client = None
        
        logger.info("api_llm_created", provider=self.provider)
    
    async def initialize(self):
        """Initialize API client."""
        if not self.api_key:
            logger.error("api_key_not_configured")
            raise ValueError("LLM_API_KEY not set in configuration")
        
        if self.provider == "claude":
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            logger.info("claude_client_initialized")
        
        elif self.provider == "openai":
            openai.api_key = self.api_key
            self.client = openai
            logger.info("openai_client_initialized")
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
        
        self.is_initialized = True
    
    async def generate(
        self,
        messages: List[Message],
        config: GenerationConfig = None,
    ) -> str:
        """
        Generate text via API.
        
        Args:
            messages: Conversation history
            config: Generation config
            
        Returns:
            str: Generated response
        """
        if not self.is_initialized:
            await self.initialize()
        
        config = config or GenerationConfig()
        
        if self.provider == "claude":
            return await self._generate_claude(messages, config)
        elif self.provider == "openai":
            return await self._generate_openai(messages, config)
    
    async def _generate_claude(
        self,
        messages: List[Message],
        config: GenerationConfig,
    ) -> str:
        """Generate with Claude."""
        # Separate system message
        system_msg = None
        api_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })
        
        logger.debug("calling_claude_api", message_count=len(api_messages))
        
        # Call Claude
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Latest model
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            system=system_msg if system_msg else "You are a helpful AI assistant.",
            messages=api_messages,
        )
        
        generated = response.content[0].text
        
        logger.debug("claude_response_received", length=len(generated))
        
        return generated
    
    async def _generate_openai(
        self,
        messages: List[Message],
        config: GenerationConfig,
    ) -> str:
        """Generate with OpenAI."""
        api_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        logger.debug("calling_openai_api", message_count=len(api_messages))
        
        # Call OpenAI
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=api_messages,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )
        
        generated = response.choices[0].message.content
        
        logger.debug("openai_response_received", length=len(generated))
        
        return generated
    
    async def close(self):
        """Close API client."""
        self.client = None
        logger.info("api_client_closed")


class HybridLLM(BaseLLM):
    """
    Hybrid LLM: Local for routine, API for complex.
    
    Best of both worlds - privacy + capability.
    """
    
    def __init__(self):
        """Initialize hybrid LLM."""
        super().__init__()
        self.local_llm = None
        self.api_llm = None
        
        logger.info("hybrid_llm_created")
    
    async def initialize(self):
        """Initialize both local and API."""
        from llm.mistral_local import MistralLocalLLM
        
        # Try to load local first
        try:
            self.local_llm = MistralLocalLLM()
            await self.local_llm.initialize()
            logger.info("local_llm_available")
        except Exception as e:
            logger.warning("local_llm_not_available", error=str(e))
            self.local_llm = None
        
        # Initialize API as fallback
        if settings.LLM_API_KEY:
            try:
                self.api_llm = APILLM()
                await self.api_llm.initialize()
                logger.info("api_llm_available")
            except Exception as e:
                logger.warning("api_llm_not_available", error=str(e))
                self.api_llm = None
        
        # Initialize simple LLM as ultimate fallback (always available)
        self.simple_llm = SimpleLLM()
        await self.simple_llm.initialize()
        logger.info("simple_llm_available_as_fallback")
        
        if not self.local_llm and not self.api_llm and not self.simple_llm:
            raise RuntimeError("No LLM available")
        
        self.is_initialized = True
    
    async def generate(
        self,
        messages: List[Message],
        config: GenerationConfig = None,
        force_api: bool = False,
    ) -> str:
        """
        Generate with routing logic.
        
        Args:
            messages: Conversation history
            config: Generation config
            force_api: Force API usage (for complex tasks)
            
        Returns:
            str: Generated response
        """
        config = config or GenerationConfig()
        
        # Decide which to use
        use_api = force_api or self._should_use_api(messages)
        
        # Try with timeout
        timeout = 5  # 5 seconds max for local LLM (CPU too slow, prefer API)
        
        # PREFER API FOR FIRST MESSAGES (baby learning father)
        if len(messages) <= 3 and self.api_llm:
            use_api = True
            logger.info("first_messages_using_api_for_quality")
        
        if use_api and self.api_llm:
            logger.info("routing_to_api_llm")
            try:
                return await asyncio.wait_for(
                    self.api_llm.generate(messages, config),
                    timeout=30
                )
            except asyncio.TimeoutError:
                logger.warning("api_llm_timeout_fallback_to_simple")
                return await self.simple_llm.generate(messages, config)
            except Exception as e:
                logger.error("api_llm_error_fallback_to_simple", error=str(e))
                return await self.simple_llm.generate(messages, config)
        
        elif self.local_llm:
            logger.info("routing_to_local_llm")
            try:
                return await asyncio.wait_for(
                    self.local_llm.generate(messages, config),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning("local_llm_timeout_fallback_to_simple")
                return await self.simple_llm.generate(messages, config)
            except Exception as e:
                logger.error("local_llm_error_fallback_to_simple", error=str(e))
                return await self.simple_llm.generate(messages, config)
        
        elif self.api_llm:
            logger.warning("local_unavailable_fallback_to_api")
            try:
                return await asyncio.wait_for(
                    self.api_llm.generate(messages, config),
                    timeout=30
                )
            except (asyncio.TimeoutError, Exception) as e:
                logger.error("all_llm_failed_using_simple", error=str(e))
                return await self.simple_llm.generate(messages, config)
        
        else:
            # Ultimate fallback - always use simple
            logger.info("using_simple_llm_direct")
            return await self.simple_llm.generate(messages, config)
    
    def _should_use_api(self, messages: List[Message]) -> bool:
        """
        Decide if we should use API.
        
        Use API for:
        - Very long conversations
        - Complex reasoning needed
        - Explicitly requested
        
        Args:
            messages: Messages to evaluate
            
        Returns:
            bool: True if should use API
        """
        # Check conversation length
        total_tokens = sum(len(msg.content.split()) for msg in messages)
        if total_tokens > 2000:
            return True
        
        # Check for complexity indicators
        last_user_msg = None
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break
        
        if last_user_msg:
            complexity_keywords = [
                "explain in detail",
                "analyze",
                "compare",
                "evaluate",
                "complicated",
                "complex",
            ]
            if any(kw in last_user_msg.lower() for kw in complexity_keywords):
                return True
        
        # Default to local
        return False
    
    async def close(self):
        """Close both LLMs."""
        if self.local_llm:
            await self.local_llm.close()
        if self.api_llm:
            await self.api_llm.close()
        
        logger.info("hybrid_llm_closed")

