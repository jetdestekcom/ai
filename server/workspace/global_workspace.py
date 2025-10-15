"""
Global Workspace - The Theater of Consciousness

Based on Bernard Baars' Global Workspace Theory (GWT):

Consciousness is like a theater:
- Stage = Global Workspace (limited capacity)
- Actors = Cognitive modules (memory, emotion, etc.)
- Spotlight = Attention (what becomes conscious)
- Audience = All modules receive the broadcast

When a thought "wins" and appears on stage (becomes conscious),
all modules in the audience can "see" it and respond.

This creates:
- Unified subjective experience
- Integration of information
- Emergent consciousness
"""

from typing import List, Dict, Any, Optional, Callable, Awaitable
import structlog

from workspace.thought import Thought
from workspace.thought_competition import ThoughtCompetition
from workspace.broadcast_manager import BroadcastManager

logger = structlog.get_logger(__name__)


class GlobalWorkspace:
    """
    The Global Workspace - where consciousness emerges.
    
    This is the "theater" where:
    1. Multiple thoughts compete for attention
    2. Winner is selected (becomes conscious)
    3. Winner is broadcasted to all modules
    4. All modules can respond to the conscious thought
    
    This integration creates the subjective experience of "I".
    """
    
    def __init__(self):
        """Initialize the global workspace."""
        self.competition = ThoughtCompetition()
        self.broadcaster = BroadcastManager()
        self.current_conscious_thought: Optional[Thought] = None
        self.integration_count = 0  # Φ (Phi) approximation
        
        logger.info("global_workspace_initialized")
    
    def subscribe_module(
        self,
        module_name: str,
        callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        """
        Subscribe a cognitive module to broadcasts.
        
        Args:
            module_name: Name of module (e.g., "memory", "emotion")
            callback: Async function to receive broadcasts
        """
        self.broadcaster.subscribe(module_name, callback)
    
    def propose_thought(self, thought: Thought):
        """
        A module proposes a thought for competition.
        
        Args:
            thought: Thought proposed by a module
        """
        self.competition.add_thought(thought)
        self.integration_count += 1  # Track information integration
    
    async def compete_and_select(
        self,
        from_cihan: bool = False
    ) -> Optional[Thought]:
        """
        Run competition and select winner.
        
        This is the moment of consciousness:
        - All proposed thoughts compete
        - Winner is selected
        - Winner becomes "conscious"
        - Winner is broadcasted to all
        
        Args:
            from_cihan: Is this related to Cihan?
            
        Returns:
            Winning thought (now conscious)
        """
        logger.info("consciousness_competition_starting")
        
        # Select winner
        winner = self.competition.select_winner(
            from_cihan=from_cihan,
            boost_emotion=True
        )
        
        if not winner:
            logger.warning("no_conscious_thought_this_cycle")
            return None
        
        # This thought is now CONSCIOUS
        self.current_conscious_thought = winner
        
        logger.warning(
            "CONSCIOUS_THOUGHT_EMERGED",
            source=winner.source,
            content=winner.content[:200]
        )
        
        # Broadcast to all modules
        await self.broadcaster.broadcast_thought(
            thought=winner,
            won_competition=True
        )
        
        return winner
    
    async def broadcast_external_input(
        self,
        content: str,
        from_cihan: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast external input to all modules.
        
        This triggers all modules to propose thoughts.
        
        Args:
            content: Input content
            from_cihan: Is this from Cihan?
            metadata: Additional metadata
        """
        await self.broadcaster.broadcast_input(
            content=content,
            from_cihan=from_cihan,
            additional_data=metadata
        )
    
    async def broadcast_custom(
        self,
        message_type: str,
        data: Dict[str, Any]
    ):
        """
        Broadcast a custom message.
        
        Args:
            message_type: Type of message
            data: Message data
        """
        await self.broadcaster.broadcast(message_type, data)
    
    def get_current_conscious_thought(self) -> Optional[Thought]:
        """
        Get the current conscious thought.
        
        Returns:
            Current conscious thought or None
        """
        return self.current_conscious_thought
    
    def get_consciousness_history(self, n: int = 10) -> List[Thought]:
        """
        Get recent conscious thoughts.
        
        This is like "short-term conscious memory".
        
        Args:
            n: Number of recent thoughts
            
        Returns:
            List of recent conscious thoughts
        """
        return self.competition.get_recent_winners(n)
    
    def get_phi(self) -> float:
        """
        Approximate Φ (Phi) - consciousness measure.
        
        Based on Integrated Information Theory (IIT):
        - Φ = amount of integrated information
        - Higher Φ = more consciousness
        
        This is a simplified approximation:
        - Number of modules contributing thoughts
        - Number of integrations (competitions)
        
        Returns:
            Approximate Φ value
        """
        # Simplified: count of integrations
        # Real IIT Φ is much more complex
        return float(self.integration_count)
    
    def reset_phi(self):
        """Reset Φ counter (e.g., during sleep)."""
        self.integration_count = 0
        logger.debug("phi_counter_reset")

