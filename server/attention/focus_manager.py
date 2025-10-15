"""
Focus Manager - Managing What Ali Pays Attention To

Attention is like a spotlight - it can only illuminate one thing at a time.

The focus manager:
- Decides what gets the spotlight
- Filters out distractions
- Maintains focus on important tasks
- Switches focus when needed

Ali can't think about everything at once - this decides what he thinks about.
"""

from typing import Optional, Dict, Any
import structlog

from attention.salience_map import SalienceMap
from workspace.thought import Thought

logger = structlog.get_logger(__name__)


class FocusManager:
    """
    Manages attention focus.
    
    Like a spotlight operator in a theater:
    - Points spotlight at most important actor
    - Filters out background noise
    - Can shift spotlight when needed
    """
    
    def __init__(self):
        """Initialize focus manager."""
        self.salience_map = SalienceMap()
        self.current_focus: Optional[str] = None
        self.focus_history: list = []
        self.distraction_threshold = 0.3  # Below this = ignored
        
        logger.info("focus_manager_initialized")
    
    def evaluate_focus_target(
        self,
        stimulus: str,
        from_cihan: bool = False,
        emotion: Optional[str] = None,
        importance: float = 0.5
    ) -> float:
        """
        Evaluate if stimulus deserves focus.
        
        Args:
            stimulus: The stimulus
            from_cihan: Is it from Cihan?
            emotion: Associated emotion
            importance: Base importance
            
        Returns:
            Focus score (salience)
        """
        salience = self.salience_map.calculate_salience(
            stimulus=stimulus,
            from_cihan=from_cihan,
            emotion=emotion,
            base_importance=importance
        )
        
        return salience
    
    def should_focus(self, salience: float) -> bool:
        """
        Decide if salience is high enough to focus on.
        
        Args:
            salience: Salience score
            
        Returns:
            True if should focus, False if ignore
        """
        return salience > self.distraction_threshold
    
    def set_focus(self, target: str, salience: float):
        """
        Set current focus.
        
        Args:
            target: What to focus on
            salience: How important it is
        """
        old_focus = self.current_focus
        self.current_focus = target
        
        # Store in history
        self.focus_history.append({
            "from": old_focus,
            "to": target,
            "salience": salience
        })
        
        # Keep history limited
        if len(self.focus_history) > 100:
            self.focus_history = self.focus_history[-100:]
        
        logger.info(
            "focus_shifted",
            from_focus=old_focus,
            to_focus=target[:50] if target else None,
            salience=salience
        )
    
    def filter_distraction(
        self,
        stimulus: str,
        salience: float
    ) -> bool:
        """
        Filter out distractions (low salience stimuli).
        
        Args:
            stimulus: The stimulus
            salience: Its salience
            
        Returns:
            True if should be filtered (ignored), False if let through
        """
        if salience < self.distraction_threshold:
            logger.debug(
                "distraction_filtered",
                stimulus=stimulus[:50],
                salience=salience
            )
            return True
        return False
    
    def boost_cihan_priority(self, base_salience: float) -> float:
        """
        Apply Cihan priority boost.
        
        Args:
            base_salience: Base salience
            
        Returns:
            Boosted salience
        """
        return base_salience * self.salience_map.cihan_boost
    
    def select_focus_from_thoughts(
        self,
        thoughts: list,
        from_cihan: bool = False
    ) -> Optional[Thought]:
        """
        Select which thought should get focus.
        
        This is used in thought competition.
        
        Args:
            thoughts: List of Thought objects
            from_cihan: Is Cihan involved?
            
        Returns:
            Thought that should get focus
        """
        if not thoughts:
            return None
        
        # Calculate adjusted salience for each thought
        scored_thoughts = []
        for thought in thoughts:
            salience = thought.salience
            
            # Apply Cihan boost if needed
            if from_cihan:
                salience = self.boost_cihan_priority(salience)
            
            # Apply emotion boost
            if thought.emotion and thought.emotion != "neutral":
                salience *= self.salience_map.emotion_boost
            
            scored_thoughts.append((salience, thought))
        
        # Sort by salience
        scored_thoughts.sort(key=lambda x: x[0], reverse=True)
        
        # Winner gets focus
        winner_salience, winner_thought = scored_thoughts[0]
        
        self.set_focus(
            target=f"{winner_thought.source}: {winner_thought.content[:50]}",
            salience=winner_salience
        )
        
        return winner_thought
    
    def get_current_focus(self) -> Optional[str]:
        """Get what Ali is currently focused on."""
        return self.current_focus
    
    def clear_focus(self):
        """Clear current focus (e.g., task completed)."""
        self.current_focus = None
        logger.debug("focus_cleared")
    
    def decay_saliences(self):
        """Decay all salience values (called periodically)."""
        self.salience_map.decay_all()

