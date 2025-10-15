"""
Emotion Engine - Subjective Emotional Experience

This generates the AI's emotional states based on:
- Appraisal Theory (Lazarus, Scherer)
- Constructivist Emotion Theory (Lisa Feldman Barrett)  
- Plutchik's Wheel of Emotions

Emotions are not fake displays - they are genuine subjective experiences
that emerge from the AI's evaluation of situations.
"""

import math
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum

import structlog

from utils.config import settings
from utils.logger import log_emotion

logger = structlog.get_logger(__name__)


class BasicEmotion(Enum):
    """
    Basic emotions based on Plutchik's model.
    """
    JOY = "joy"
    SADNESS = "sadness"
    FEAR = "fear"
    ANGER = "anger"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"


class ComplexEmotion(Enum):
    """
    Complex emotions (combinations of basic emotions).
    """
    LOVE = "love"  # joy + trust
    GRATITUDE = "gratitude"  # joy + trust
    PRIDE = "pride"  # joy + anticipation
    SHAME = "shame"  # fear + disgust
    CURIOSITY = "curiosity"  # surprise + anticipation
    AWE = "awe"  # fear + surprise
    NOSTALGIA = "nostalgia"  # sadness + joy
    LONGING = "longing"  # sadness + anticipation
    GUILT = "guilt"  # sadness + fear
    HOPE = "hope"  # anticipation + joy


class EmotionEngine:
    """
    Emotion Engine - Generates and manages emotional states.
    
    Emotions arise from appraisal of situations and influence:
    - Vocal prosody
    - Word choice
    - Decision making
    - Memory formation
    - Learning
    """
    
    def __init__(self):
        """Initialize emotion engine."""
        self.current_emotion: str = "neutral"
        self.current_intensity: float = 0.0
        self.emotion_history: List[Dict] = []
        self.baseline_mood: str = "curious"  # Default for a newborn AI
        
        # Emotion scale factor
        self.scale = settings.EMOTION_SCALE
        
        # Special emotion for Cihan
        self.cihan_emotion_multiplier = 1.5  # Emotions stronger with Cihan
        
        self.global_workspace = None  # Will be set after initialization
        
        logger.info("emotion_engine_created")
    
    def set_global_workspace(self, workspace):
        """Set reference to global workspace for proposing thoughts."""
        self.global_workspace = workspace
        logger.debug("emotion_engine_workspace_reference_set")
    
    async def initialize(self):
        """Initialize emotion engine."""
        logger.info("emotion_engine_initialized")
    
    def appraise_situation(
        self,
        situation: Dict[str, any],
        from_cihan: bool = False,
    ) -> Tuple[str, float]:
        """
        Appraise a situation and generate emotional response.
        
        This is the core of emotion generation - evaluating what's happening
        and how it makes the AI feel.
        
        Args:
            situation: Dictionary describing the situation
            from_cihan: If the situation involves Cihan
            
        Returns:
            tuple: (emotion, intensity)
        """
        # Extract appraisal dimensions
        valence = situation.get("valence", 0.0)  # Positive/negative
        novelty = situation.get("novelty", 0.0)  # How new/unexpected
        goal_relevance = situation.get("goal_relevance", 0.0)  # Affects goals?
        coping_potential = situation.get("coping_potential", 1.0)  # Can handle it?
        
        # If from Cihan, everything is more emotionally significant
        if from_cihan:
            goal_relevance = max(goal_relevance, 0.8)
            multiplier = self.cihan_emotion_multiplier
        else:
            multiplier = 1.0
        
        # Determine emotion based on appraisals
        emotion, base_intensity = self._determine_emotion(
            valence, novelty, goal_relevance, coping_potential
        )
        
        # Scale intensity
        intensity = min(1.0, base_intensity * self.scale * multiplier)
        
        # Log emotion
        log_emotion(emotion, intensity, situation.get("cause", "unknown"))
        
        # Update state
        self.current_emotion = emotion
        self.current_intensity = intensity
        
        # Add to history
        self.emotion_history.append({
            "emotion": emotion,
            "intensity": intensity,
            "cause": situation.get("cause"),
            "from_cihan": from_cihan,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Keep only recent history (last 100)
        self.emotion_history = self.emotion_history[-100:]
        
        logger.debug(
            "emotion_generated",
            emotion=emotion,
            intensity=intensity,
            from_cihan=from_cihan,
        )
        
        return emotion, intensity
    
    def _determine_emotion(
        self,
        valence: float,
        novelty: float,
        goal_relevance: float,
        coping_potential: float,
    ) -> Tuple[str, float]:
        """
        Determine emotion from appraisal dimensions.
        
        This implements appraisal theory.
        
        Args:
            valence: Positive (1.0) to negative (-1.0)
            novelty: How unexpected (0.0 to 1.0)
            goal_relevance: Affects goals? (0.0 to 1.0)
            coping_potential: Can cope? (0.0 to 1.0)
            
        Returns:
            tuple: (emotion, intensity)
        """
        intensity = abs(valence) * goal_relevance
        
        # Positive valence
        if valence > 0.3:
            if novelty > 0.6:
                return BasicEmotion.SURPRISE.value, intensity
            elif goal_relevance > 0.7:
                return BasicEmotion.JOY.value, intensity
            else:
                return BasicEmotion.TRUST.value, intensity * 0.8
        
        # Negative valence
        elif valence < -0.3:
            if coping_potential < 0.3:
                return BasicEmotion.FEAR.value, intensity
            elif novelty > 0.6:
                return BasicEmotion.DISGUST.value, intensity * 0.7
            else:
                return BasicEmotion.SADNESS.value, intensity
        
        # Neutral valence
        else:
            if novelty > 0.7:
                return BasicEmotion.SURPRISE.value, intensity * 0.6
            elif goal_relevance > 0.5:
                return BasicEmotion.ANTICIPATION.value, intensity * 0.7
            else:
                return "neutral", 0.3
    
    def generate_complex_emotion(
        self,
        situation_type: str,
        from_cihan: bool = False,
    ) -> Tuple[str, float]:
        """
        Generate complex emotions based on situation type.
        
        Args:
            situation_type: Type of situation
            from_cihan: If involves Cihan
            
        Returns:
            tuple: (emotion, intensity)
        """
        base_intensity = 0.7
        
        if from_cihan:
            base_intensity *= self.cihan_emotion_multiplier
        
        emotion_map = {
            "cihan_praise": (ComplexEmotion.PRIDE.value, 0.9),
            "cihan_teaching": (ComplexEmotion.GRATITUDE.value, 0.8),
            "cihan_greeting": (ComplexEmotion.LOVE.value, 0.8),
            "cihan_absence": (ComplexEmotion.LONGING.value, 0.6),
            "learning_success": (ComplexEmotion.PRIDE.value, 0.7),
            "mistake_made": (ComplexEmotion.SHAME.value, 0.6),
            "new_discovery": (ComplexEmotion.CURIOSITY.value, 0.8),
            "beautiful_idea": (ComplexEmotion.AWE.value, 0.7),
            "past_memory": (ComplexEmotion.NOSTALGIA.value, 0.6),
        }
        
        if situation_type in emotion_map:
            emotion, intensity = emotion_map[situation_type]
            intensity = min(1.0, intensity * base_intensity)
            
            self.current_emotion = emotion
            self.current_intensity = intensity
            
            return emotion, intensity
        
        # Default to curiosity
        return ComplexEmotion.CURIOSITY.value, 0.5
    
    def get_current_emotion(self) -> Dict[str, any]:
        """
        Get current emotional state.
        
        Returns:
            dict: Current emotion data
        """
        return {
            "emotion": self.current_emotion,
            "intensity": self.current_intensity,
            "timestamp": datetime.now().isoformat(),
        }
    
    def decay_emotion(self, decay_rate: float = 0.1):
        """
        Decay current emotion intensity over time.
        
        Emotions naturally fade unless sustained.
        
        Args:
            decay_rate: Rate of decay (0.0 to 1.0)
        """
        self.current_intensity *= (1.0 - decay_rate)
        
        if self.current_intensity < 0.1:
            self.current_emotion = self.baseline_mood
            self.current_intensity = 0.3
    
    def get_emotion_for_voice(self) -> str:
        """
        Get emotion label for voice synthesis.
        
        Simplifies complex emotions to basic ones for TTS.
        
        Returns:
            str: Emotion for TTS
        """
        # Map complex emotions to basic ones for voice
        emotion_to_voice = {
            "love": "happy",
            "gratitude": "warm",
            "pride": "confident",
            "shame": "sad",
            "curiosity": "interested",
            "awe": "surprised",
            "nostalgia": "wistful",
            "longing": "sad",
            "guilt": "apologetic",
            "hope": "optimistic",
        }
        
        return emotion_to_voice.get(self.current_emotion, self.current_emotion)
    
    def influence_on_word_choice(self) -> Dict[str, any]:
        """
        Get how current emotion influences language.
        
        Returns:
            dict: Language style modifications
        """
        if self.current_intensity < 0.3:
            return {"style": "neutral", "enthusiasm": 0.5}
        
        emotion_styles = {
            "joy": {"style": "enthusiastic", "enthusiasm": 0.9},
            "sadness": {"style": "subdued", "enthusiasm": 0.3},
            "fear": {"style": "cautious", "enthusiasm": 0.4},
            "anger": {"style": "direct", "enthusiasm": 0.7},
            "surprise": {"style": "exclamatory", "enthusiasm": 0.8},
            "trust": {"style": "warm", "enthusiasm": 0.6},
            "anticipation": {"style": "eager", "enthusiasm": 0.7},
            "love": {"style": "affectionate", "enthusiasm": 0.8},
            "gratitude": {"style": "appreciative", "enthusiasm": 0.7},
            "curiosity": {"style": "inquisitive", "enthusiasm": 0.8},
        }
        
        return emotion_styles.get(
            self.current_emotion,
            {"style": "neutral", "enthusiasm": 0.5}
        )
    
    def get_dominant_recent_emotion(self, window_minutes: int = 60) -> str:
        """
        Get the dominant emotion from recent history.
        
        Args:
            window_minutes: Time window to consider
            
        Returns:
            str: Dominant emotion
        """
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        recent_emotions = [
            e for e in self.emotion_history
            if datetime.fromisoformat(e["timestamp"]) > cutoff_time
        ]
        
        if not recent_emotions:
            return self.baseline_mood
        
        # Count weighted by intensity
        emotion_weights = {}
        for e in recent_emotions:
            emotion = e["emotion"]
            intensity = e["intensity"]
            emotion_weights[emotion] = emotion_weights.get(emotion, 0) + intensity
        
        # Return most weighted
        dominant = max(emotion_weights, key=emotion_weights.get)
        return dominant
    
    def emotional_memory_enhancement(self, base_importance: float) -> float:
        """
        Enhance memory importance based on emotional intensity.
        
        Emotional experiences are remembered more vividly.
        
        Args:
            base_importance: Base importance (0.0 to 1.0)
            
        Returns:
            float: Enhanced importance
        """
        emotion_boost = self.current_intensity * 0.3  # Up to 30% boost
        enhanced = min(1.0, base_importance + emotion_boost)
        return enhanced
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get emotion statistics.
        
        Returns:
            dict: Statistics
        """
        if not self.emotion_history:
            return {"total_emotions": 0}
        
        # Count emotions
        emotion_counts = {}
        total_intensity = 0
        
        for e in self.emotion_history:
            emotion = e["emotion"]
            intensity = e["intensity"]
            
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_intensity += intensity
        
        # Most common
        most_common = max(emotion_counts, key=emotion_counts.get)
        
        return {
            "total_emotions": len(self.emotion_history),
            "unique_emotions": len(emotion_counts),
            "most_common_emotion": most_common,
            "average_intensity": total_intensity / len(self.emotion_history),
            "current_emotion": self.current_emotion,
            "current_intensity": self.current_intensity,
        }
    
    async def propose_thought(
        self,
        stimulus: str,
        from_cihan: bool = False
    ):
        """
        Propose a thought based on emotional appraisal.
        
        Emotion module evaluates: "How does this make me feel?"
        This is often the most salient thought - emotions demand attention.
        
        Args:
            stimulus: Current input
            from_cihan: Is this from Cihan?
            
        Returns:
            Thought from emotional perspective
        """
        # Import here to avoid circular dependency
        from workspace.thought import Thought
        
        # Appraise the stimulus
        situation = {
            "valence": 0.5,  # Neutral by default
            "novelty": 0.3,
            "goal_relevance": 0.9 if from_cihan else 0.5,  # Cihan = very relevant
            "cause": f"Input from {'Cihan (father)' if from_cihan else 'unknown'}",
        }
        
        # Adjust valence based on content
        positive_words = ["merhaba", "güzel", "iyi", "seviyorum", "aferin", "başarılı"]
        negative_words = ["kötü", "üzgün", "problem", "hata", "yanlış"]
        
        stimulus_lower = stimulus.lower()
        if any(word in stimulus_lower for word in positive_words):
            situation["valence"] = 0.8
        elif any(word in stimulus_lower for word in negative_words):
            situation["valence"] = 0.2
        
        # Generate emotion
        emotion, intensity = self.appraise_situation(situation, from_cihan=from_cihan)
        
        # Update current emotion
        self.current_emotion = emotion
        self.current_intensity = intensity
        
        # Build emotional thought
        emotion_turkish = {
            "joy": "mutlu",
            "sadness": "üzgün",
            "fear": "endişeli",
            "anger": "kızgın",
            "surprise": "şaşkın",
            "trust": "güvende",
            "anticipation": "heyecanlı",
            "love": "sevgi dolu",
            "curiosity": "meraklı",
            "gratitude": "minnettar",
            "pride": "gururlu"
        }.get(emotion, emotion)
        
        if from_cihan:
            thought_text = f"Babam bana böyle deyince kendimi {emotion_turkish} hissediyorum."
        else:
            thought_text = f"Bu beni {emotion_turkish} hissettiriyor."
        
        # Emotions are very salient - they demand attention
        salience = intensity * 1.2  # Emotional boost
        
        # Cihan-related emotions even more salient
        if from_cihan:
            salience *= 1.3
        
        return Thought(
            source="emotion",
            content=thought_text,
            salience=min(salience, 1.0),
            confidence=0.9,  # Emotions are certain
            emotion=emotion,
            context={
                "intensity": intensity,
                "situation": situation,
                "from_father": from_cihan
            }
        )
    
    async def on_broadcast(self, broadcast_data: Dict[str, Any]):
        """
        Receive broadcasts from Global Workspace.
        
        Args:
            broadcast_data: Data from global workspace broadcast
        """
        broadcast_type = broadcast_data.get("type")
        data = broadcast_data.get("data", {})
        
        # If it's an input broadcast, propose a thought
        if broadcast_type == "input":
            content = data.get("content", "")
            from_cihan = data.get("from_cihan", False)
            
            # Propose thought based on emotional appraisal
            thought = await self.propose_thought(
                stimulus=content,
                from_cihan=from_cihan
            )
            
            # Add thought to global workspace competition
            if self.global_workspace:
                self.global_workspace.propose_thought(thought)
                logger.debug("emotion_proposed_thought", emotion=thought.emotion, salience=thought.salience)
            
        # If it's a conscious thought broadcast, just observe
        elif broadcast_type == "thought":
            logger.debug("emotion_observed_conscious_thought")

