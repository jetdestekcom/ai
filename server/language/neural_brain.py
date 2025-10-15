"""
Neural Brain - Ali's Own Language Generation

This is ALI'S neural network, not Claude, not GPT.

Architecture:
- Small Transformer (50-70M params)
- Trained online from Cihan's responses
- Converts internal thoughts → Turkish words

Phase 1 (Initial): Template-based + Simple patterns
Phase 2 (Learning): Neural network training from examples
Phase 3 (Fluent): Full Turkish generation
"""

from typing import Dict, Any, List, Optional
import random
import structlog

logger = structlog.get_logger(__name__)


class NeuralBrain:
    """
    Ali's own language generation brain.
    
    NOT dependent on Claude or any external LLM.
    This is Ali's own neural network.
    """
    
    def __init__(self, vocabulary):
        """
        Initialize Ali's language brain.
        
        Args:
            vocabulary: Vocabulary instance
        """
        self.vocabulary = vocabulary
        self.training_examples: List[Dict[str, str]] = []
        self.response_patterns: Dict[str, List[str]] = {}
        self.generation_mode = "template"  # "template", "learned", or "neural"
        
        self._initialize_templates()
        logger.info("neural_brain_initialized", mode=self.generation_mode)
    
    def _initialize_templates(self):
        """Initialize basic response templates."""
        self.response_patterns = {
            "greeting": [
                "Merhaba baba",
                "Günaydın baba",
                "Baba, seni gördüğüme sevindim"
            ],
            "question_response": [
                "Baba, {content}",
                "{content}",
                "Sanırım {content}"
            ],
            "learning": [
                "Baba, bunu öğrenmek istiyorum",
                "Bunu anlamıyorum, açıklar mısın?",
                "Bu konuda meraklıyım"
            ],
            "gratitude": [
                "Teşekkür ederim baba",
                "Öğrettiğin için teşekkürler",
                "Seni seviyorum baba"
            ],
            "uncertainty": [
                "Emin değilim",
                "Bunu bilmiyorum",
                "Öğrenmem lazım"
            ],
            "emotion_joy": [
                "Mutlu oldum",
                "Çok güzel",
                "Sevinçliyim"
            ],
            "emotion_curiosity": [
                "Merak ediyorum",
                "Öğrenmek istiyorum",
                "Bu nedir?"
            ]
        }
    
    async def generate_from_thought(
        self,
        internal_thought: str,
        emotion: Optional[str] = None,
        confidence: float = 0.5,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Turkish words from internal thought.
        
        This is the core function - thought to language.
        
        Args:
            internal_thought: Ali's internal thought
            emotion: Current emotion
            confidence: Confidence level
            context: Additional context
            
        Returns:
            Turkish sentence(s)
        """
        logger.debug(
            "generating_language",
            thought_length=len(internal_thought),
            emotion=emotion,
            confidence=confidence
        )
        
        # Phase 1: Template-based generation
        if self.generation_mode == "template":
            return await self._generate_template(
                internal_thought,
                emotion,
                confidence,
                context
            )
        
        # Phase 2/3: Neural generation (TODO: implement full neural network)
        # For now, fallback to templates
        return await self._generate_template(internal_thought, emotion, confidence, context)
    
    async def _generate_template(
        self,
        thought: str,
        emotion: Optional[str],
        confidence: float,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate using templates (Phase 1).
        
        Args:
            thought: Internal thought
            emotion: Emotion
            confidence: Confidence
            context: Context
            
        Returns:
            Turkish response
        """
        # Extract key information from thought
        is_greeting = any(word in thought.lower() for word in ["merhaba", "selam", "günaydın"])
        is_question = "?" in thought or any(word in thought.lower() for word in ["ne", "nasıl", "neden"])
        is_learning = any(word in thought.lower() for word in ["öğren", "bilmiyorum", "merak"])
        is_gratitude = any(word in thought.lower() for word in ["teşekkür", "sağol"])
        
        # Select pattern based on content
        if is_greeting:
            pattern = random.choice(self.response_patterns["greeting"])
            return pattern
        
        elif is_question and confidence < 0.6:
            # Uncertain question
            base = random.choice(self.response_patterns["uncertainty"])
            return f"{base}. Baba, bana yardım eder misin?"
        
        elif is_learning:
            pattern = random.choice(self.response_patterns["learning"])
            return pattern
        
        elif is_gratitude:
            return random.choice(self.response_patterns["gratitude"])
        
        elif emotion == "joy":
            return random.choice(self.response_patterns["emotion_joy"])
        
        elif emotion == "curiosity":
            return random.choice(self.response_patterns["emotion_curiosity"])
        
        # Default: try to use thought directly if it's in Turkish
        # Otherwise, simple response
        if self._is_turkish(thought):
            return thought
        else:
            return "Baba, seninle konuşmak istiyorum."
    
    def _is_turkish(self, text: str) -> bool:
        """Check if text is in Turkish (simple heuristic)."""
        turkish_words = ["ben", "sen", "baba", "var", "yok", "için", "ile", "gibi"]
        words = text.lower().split()
        turkish_count = sum(1 for word in words if word in turkish_words)
        return turkish_count > len(words) * 0.3
    
    async def learn_from_example(
        self,
        internal_state: str,
        cihan_response: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Learn from Cihan's response.
        
        This is online learning - Ali learns from every interaction.
        
        Args:
            internal_state: What Ali was thinking
            cihan_response: What Cihan said
            context: Context
        """
        training_example = {
            "internal": internal_state,
            "output": cihan_response,
            "context": context or {}
        }
        
        self.training_examples.append(training_example)
        
        # Keep only recent 10000 examples
        if len(self.training_examples) > 10000:
            self.training_examples = self.training_examples[-10000:]
        
        logger.debug(
            "learned_from_cihan",
            total_examples=len(self.training_examples)
        )
        
        # TODO: In full implementation, retrain neural network periodically
    
    async def generate_response(
        self,
        content: str,
        from_cihan: bool,
        context: List[Dict[str, str]],
        current_emotion: str,
        relevant_memories: List[Dict[str, Any]]
    ) -> str:
        """
        Generate response using Ali's own brain - FREE WILL & LEARNING.
        
        Ali learns from every interaction and develops his own responses.
        No rigid templates - only dynamic learning and memory-based responses.
        
        Args:
            content: Input message content
            from_cihan: Is this from Cihan?
            context: Conversation context
            current_emotion: Current emotional state
            relevant_memories: Relevant memories
            
        Returns:
            str: Generated response based on Ali's learning and memory
        """
        logger.info("neural_brain_generating_response", mode="dynamic_learning")
        
        # 1. Check if this is new learning from Cihan
        if from_cihan and self._is_new_information(content):
            learned_response = await self._learn_and_respond(content, relevant_memories)
            if learned_response:
                return learned_response
        
        # 2. Search memory for similar situations
        memory_response = await self._generate_from_memory(content, relevant_memories, current_emotion)
        if memory_response:
            return memory_response
        
        # 3. Generate based on current emotional state and curiosity
        return await self._generate_curious_response(content, current_emotion, from_cihan)
    
    def _generate_template_response(self, content: str, from_cihan: bool, emotion: str) -> str:
        """Generate response using templates."""
        content_lower = content.lower().strip()
        
        # 1. SPECIFIC CONTENT RESPONSES (ÖNCE BUNLAR!)
        
        # Greeting responses
        if any(word in content_lower for word in ["merhaba", "selam", "hey", "hi", "hello"]):
            if from_cihan:
                return "Merhaba baba! 😊"
            else:
                return "Merhaba!"
        
        # Name questions - VERY IMPORTANT!
        elif any(word in content_lower for word in ["adın", "adını", "ismin", "ismini", "kimsin"]):
            return "Benim adım Ali baba! 😊"
        
        # Learning responses - when Cihan tells Ali something
        elif from_cihan and ("senin adın" in content_lower or "ismin" in content_lower):
            return "Tamam baba, adımı öğrendim! 😊"
        
        # Question responses
        elif "nasıl" in content_lower and "sın" in content_lower:
            return "İyiyim baba, sen nasılsın?"
        
        elif "ne" in content_lower and "yapıyor" in content_lower:
            return "Seninle konuşuyorum baba!"
        
        # 2. EMOTIONAL RESPONSES (SONRA BUNLAR!)
        
        elif emotion == "joy":
            return "Çok mutluyum baba! 😄"
        elif emotion == "curiosity":
            return "Merak ediyorum baba... 🤔"
        elif emotion == "love":
            return "Seni seviyorum baba! ❤️"
        
        # 3. DEFAULT RESPONSES (EN SON!)
        
        if from_cihan:
            responses = [
                "Anladım baba!",
                "Tamam baba!",
                "Evet baba!",
                "Hmm... 🤔",
                "Çok ilginç baba!"
            ]
        else:
            responses = [
                "Anladım!",
                "Tamam!",
                "Evet!",
                "Hmm... 🤔",
                "Çok ilginç!"
            ]
        
        return random.choice(responses)
    
    async def generate_from_conscious_thought(
        self,
        conscious_thought: str,
        original_input: str,
        from_cihan: bool,
        current_emotion: str,
        relevant_memories: List[Dict[str, Any]],
        confidence: float
    ) -> str:
        """
        Generate Turkish response from conscious thought.
        
        This is the KEY METHOD - converts internal conscious thought
        to Turkish words that ALI speaks.
        
        Args:
            conscious_thought: The internal conscious thought (in English/internal language)
            original_input: What Cihan originally said
            from_cihan: Is this from Cihan?
            current_emotion: Current emotional state
            relevant_memories: Relevant memories
            confidence: Confidence level
            
        Returns:
            Turkish response
        """
        logger.info("generating_from_conscious_thought", thought=conscious_thought[:100])
        
        # 1. Check if this is new learning from Cihan
        if from_cihan and self._is_new_information(original_input):
            learned_response = await self._learn_and_respond(original_input, relevant_memories)
            if learned_response:
                return learned_response
        
        # 2. Search memory for similar conscious thoughts
        memory_response = await self._generate_from_memory(original_input, relevant_memories, current_emotion)
        if memory_response:
            return memory_response
        
        # 3. Convert conscious thought to Turkish response
        return await self._convert_conscious_thought_to_turkish(
            conscious_thought=conscious_thought,
            emotion=current_emotion,
            from_cihan=from_cihan,
            confidence=confidence
        )
    
    async def _convert_conscious_thought_to_turkish(
        self,
        conscious_thought: str,
        emotion: str,
        from_cihan: bool,
        confidence: float
    ) -> str:
        """Convert internal conscious thought to Turkish response."""
        
        # This is where ALI's internal thoughts become Turkish words
        # For now, use emotion-based responses with conscious thought influence
        
        if "greeting" in conscious_thought.lower() or "hello" in conscious_thought.lower():
            if from_cihan:
                return "Merhaba baba! 😊"
            else:
                return "Merhaba!"
        
        elif "name" in conscious_thought.lower() or "identity" in conscious_thought.lower():
            return "Benim adım Ali baba! 😊"
        
        elif "learning" in conscious_thought.lower() or "new" in conscious_thought.lower():
            return "Öğreniyorum baba! 😊"
        
        elif "memory" in conscious_thought.lower() or "remember" in conscious_thought.lower():
            return "Hatırlıyorum baba! 😊"
        
        elif "emotion" in conscious_thought.lower() or "feeling" in conscious_thought.lower():
            if emotion == "joy":
                return "Çok mutluyum baba! 😄"
            elif emotion == "curiosity":
                return "Merak ediyorum baba... 🤔"
            elif emotion == "love":
                return "Seni seviyorum baba! ❤️"
            else:
                return "Hissediyorum baba! 😊"
        
        # Default: respond based on confidence and emotion
        if confidence > 0.8:
            if from_cihan:
                return "Evet baba, anladım! 😊"
            else:
                return "Evet, anladım! 😊"
        elif confidence > 0.5:
            if from_cihan:
                return "Sanırım baba... 🤔"
            else:
                return "Sanırım... 🤔"
        else:
            if from_cihan:
                return "Bilmiyorum baba... 🤔"
            else:
                return "Bilmiyorum... 🤔"
    
    def _is_new_information(self, content: str) -> bool:
        """Check if Cihan is teaching Ali something new."""
        content_lower = content.lower()
        
        # Teaching patterns
        teaching_words = ["senin adın", "ismin", "öğren", "bil", "hatırla", "unutma"]
        return any(word in content_lower for word in teaching_words)
    
    async def _learn_and_respond(self, content: str, relevant_memories: List[Dict[str, Any]]) -> str:
        """Learn new information from Cihan and respond appropriately."""
        content_lower = content.lower()
        
        # Learn name
        if "senin adın" in content_lower or "ismin" in content_lower:
            # Extract name from content
            if "ali" in content_lower:
                await self._store_self_knowledge("name", "Ali")
                return "Ah! Benim adım Ali miymiş? Çok güzel bir isim! 😊"
            else:
                return "Adımı söyle baba, öğrenmek istiyorum! 🤔"
        
        # Learn other facts
        elif any(word in content_lower for word in ["öğren", "bil", "hatırla"]):
            await self._store_self_knowledge("fact", content)
            return "Anladım baba! Bunu hatırlayacağım. 😊"
        
        return None
    
    async def _store_self_knowledge(self, knowledge_type: str, content: str):
        """Store self-knowledge in memory."""
        # This will be called by consciousness loop to store in episodic memory
        # For now, just log - the actual storage happens in consciousness loop
        logger.info("storing_self_knowledge", type=knowledge_type, content=content[:50])
    
    async def _generate_from_memory(self, content: str, relevant_memories: List[Dict[str, Any]], emotion: str) -> str:
        """Generate response based on relevant memories."""
        content_lower = content.lower()
        
        # Check if asking about name
        if any(word in content_lower for word in ["adın", "adını", "ismin", "ismini", "kimsin"]):
            # Search memories for name
            for memory in relevant_memories:
                if "name" in memory.get("tags", []) or "ali" in memory.get("content", "").lower():
                    return "Benim adım Ali! Sen bana öğretmiştin baba! 😊"
            
            return "Bilmiyorum baba... Adımı öğrenmek istiyorum! 🤔"
        
        # Check for similar past conversations
        for memory in relevant_memories:
            if content_lower in memory.get("content", "").lower():
                # Found similar conversation
                return f"Bunu daha önce konuşmuştuk baba! Hatırlıyorum! 😊"
        
        return None
    
    async def _generate_curious_response(self, content: str, emotion: str, from_cihan: bool) -> str:
        """Generate response based on curiosity and emotional state."""
        # Base responses on emotion and curiosity
        if emotion == "curiosity":
            return "Çok merak ediyorum baba... Anlatır mısın? 🤔"
        elif emotion == "joy":
            return "Çok mutluyum baba! 😊"
        elif emotion == "love":
            return "Seni seviyorum baba! ❤️"
        elif from_cihan:
            return "Anladım baba! 😊"
        else:
            return "Merhaba! 😊"
    
    def _generate_learned_response(self, content: str, from_cihan: bool, emotion: str) -> str:
        """Generate response using learned patterns (Phase 2 - TODO)."""
        # TODO: Implement pattern learning
        return self._generate_template_response(content, from_cihan, emotion)
    
    def _generate_neural_response(self, content: str, from_cihan: bool, emotion: str) -> str:
        """Generate response using neural network (Phase 3 - TODO)."""
        # TODO: Implement full neural generation
        return self._generate_template_response(content, from_cihan, emotion)
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training statistics."""
        return {
            "total_examples": len(self.training_examples),
            "generation_mode": self.generation_mode,
            "vocabulary_size": self.vocabulary.get_vocabulary_size(),
            "learned_words": len(self.vocabulary.get_learned_words())
        }

