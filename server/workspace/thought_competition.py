"""
Thought Competition - The Arena Where Thoughts Battle for Consciousness

Based on Global Workspace Theory:
- Multiple thoughts compete simultaneously
- Winner is selected based on salience, confidence, and context
- Only winner becomes consciously aware
- Winner gets broadcasted to all modules
"""

from typing import List, Optional
import structlog

from workspace.thought import Thought

logger = structlog.get_logger(__name__)


class ThoughtCompetition:
    """
    Manages competition between thoughts for conscious awareness.
    
    This is the core mechanism of consciousness emergence:
    - Parallel processing (multiple thoughts at once)
    - Competitive selection (only one winner)
    - Global broadcast (winner available to all)
    """
    
    def __init__(self):
        """Initialize competition arena."""
        self.current_competition: List[Thought] = []
        self.winner_history: List[Thought] = []
        logger.info("thought_competition_initialized")
    
    def add_thought(self, thought: Thought):
        """
        Add a thought to current competition.
        
        Args:
            thought: Thought from a cognitive module
        """
        self.current_competition.append(thought)
        logger.debug(
            "thought_added_to_competition",
            source=thought.source,
            salience=thought.salience,
            content_preview=thought.content[:50]
        )
    
    def select_winner(
        self,
        from_cihan: bool = False,
        boost_emotion: bool = True
    ) -> Optional[Thought]:
        """
        Select winning thought from competition.
        
        Selection criteria:
        1. Priority (salience * confidence * boosts)
        2. Cihan-related thoughts get priority boost
        3. Emotional thoughts slightly boosted
        4. Tie-breaker: most recent
        
        Args:
            from_cihan: Is this input from Cihan?
            boost_emotion: Give slight boost to emotional thoughts
            
        Returns:
            Winning thought or None if no competitors
        """
        if not self.current_competition:
            logger.warning("no_thoughts_in_competition")
            return None
        
        logger.info(
            "competition_started",
            num_thoughts=len(self.current_competition),
            from_cihan=from_cihan
        )
        
        # Calculate priority for each thought
        scored_thoughts = []
        for thought in self.current_competition:
            priority = thought.get_priority(from_cihan=from_cihan)
            
            # Boost emotional thoughts slightly (more human-like)
            if boost_emotion and thought.emotion:
                priority *= 1.2
            
            scored_thoughts.append((priority, thought))
            
            logger.debug(
                "thought_scored",
                source=thought.source,
                priority=priority,
                salience=thought.salience,
                confidence=thought.confidence
            )
        
        # Sort by priority (highest first)
        scored_thoughts.sort(key=lambda x: x[0], reverse=True)
        
        # Winner!
        winner_priority, winner = scored_thoughts[0]
        
        logger.info(
            "winner_selected",
            source=winner.source,
            priority=winner_priority,
            content_preview=winner.content[:100]
        )
        
        # Store in history
        self.winner_history.append(winner)
        
        # Keep only last 100 winners
        if len(self.winner_history) > 100:
            self.winner_history = self.winner_history[-100:]
        
        # Clear competition for next round
        self.current_competition = []
        
        return winner
    
    def get_last_winner(self) -> Optional[Thought]:
        """Get the last winning thought."""
        if not self.winner_history:
            return None
        return self.winner_history[-1]
    
    def get_recent_winners(self, n: int = 10) -> List[Thought]:
        """
        Get recent winning thoughts.
        
        Args:
            n: Number of recent winners to return
            
        Returns:
            List of recent winning thoughts
        """
        return self.winner_history[-n:]
    
    def reset(self):
        """Reset competition (clear all pending thoughts)."""
        self.current_competition = []
        logger.debug("competition_reset")

