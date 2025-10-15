"""
Salience Map - Priority Map of What Deserves Attention

A salience map tracks how "important" or "urgent" different stimuli are.

High salience = Demands attention
Low salience = Can be ignored

Factors affecting salience:
- From Cihan? → MAX salience
- Emotional? → Higher salience
- Novel/surprising? → Higher salience
- Repetitive/expected? → Lower salience
"""

from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class SalienceMap:
    """
    Tracks salience (importance/urgency) of different stimuli.
    
    This is like a "priority map" of what deserves attention.
    """
    
    def __init__(self):
        """Initialize salience map."""
        self.stimuli_salience: Dict[str, float] = {}
        self.base_salience = 0.5
        
        # Salience modifiers
        self.cihan_boost = 2.0  # Cihan gets 2x boost
        self.emotion_boost = 1.3  # Emotional content gets 1.3x
        self.novelty_boost = 1.5  # Novel stimuli get 1.5x
        self.repetition_decay = 0.8  # Repeated stimuli decay
        
        logger.info("salience_map_initialized")
    
    def calculate_salience(
        self,
        stimulus: str,
        from_cihan: bool = False,
        emotion: Optional[str] = None,
        is_novel: bool = False,
        is_repetitive: bool = False,
        base_importance: float = 0.5
    ) -> float:
        """
        Calculate salience for a stimulus.
        
        Args:
            stimulus: The stimulus
            from_cihan: Is it from Cihan?
            emotion: Associated emotion
            is_novel: Is it novel/surprising?
            is_repetitive: Is it repetitive?
            base_importance: Base importance (0-1)
            
        Returns:
            Salience score (0-2+, can exceed 1)
        """
        salience = base_importance
        
        # Cihan boost - HIGHEST PRIORITY
        if from_cihan:
            salience *= self.cihan_boost
            logger.debug("cihan_boost_applied", original=base_importance, boosted=salience)
        
        # Emotion boost
        if emotion and emotion != "neutral":
            salience *= self.emotion_boost
        
        # Novelty boost
        if is_novel:
            salience *= self.novelty_boost
        
        # Repetition decay
        if is_repetitive:
            salience *= self.repetition_decay
        
        # Store in map
        self.stimuli_salience[stimulus[:100]] = salience  # Truncate key
        
        return salience
    
    def update_salience(self, stimulus_key: str, new_salience: float):
        """
        Update salience for a stimulus.
        
        Args:
            stimulus_key: Stimulus identifier
            new_salience: New salience value
        """
        self.stimuli_salience[stimulus_key] = new_salience
    
    def get_salience(self, stimulus_key: str) -> float:
        """
        Get current salience for a stimulus.
        
        Args:
            stimulus_key: Stimulus identifier
            
        Returns:
            Current salience or base_salience
        """
        return self.stimuli_salience.get(stimulus_key, self.base_salience)
    
    def get_top_salient(self, n: int = 5) -> list:
        """
        Get top N most salient stimuli.
        
        Args:
            n: Number of top stimuli
            
        Returns:
            List of (stimulus, salience) tuples
        """
        sorted_stimuli = sorted(
            self.stimuli_salience.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_stimuli[:n]
    
    def decay_all(self, decay_factor: float = 0.95):
        """
        Decay all salience values over time.
        
        This simulates attention fading from past stimuli.
        
        Args:
            decay_factor: Multiplication factor (< 1)
        """
        for key in self.stimuli_salience:
            self.stimuli_salience[key] *= decay_factor
        
        # Remove very low salience items
        self.stimuli_salience = {
            k: v for k, v in self.stimuli_salience.items()
            if v > 0.01
        }
        
        logger.debug("salience_decayed", remaining=len(self.stimuli_salience))

