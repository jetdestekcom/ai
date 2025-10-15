"""
Value Learning from Cihan - The Foundation of Morality

The AI learns values, ethics, and morals from Cihan through:
1. Direct teaching
2. Observing Cihan's reactions
3. Corrections
4. Approval/disapproval
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)


class ValueLearning:
    """
    Value Learning System - Learn morality from Cihan.
    
    This is how the AI develops its ethical framework.
    """
    
    def __init__(self, consciousness):
        """
        Initialize value learning.
        
        Args:
            consciousness: The consciousness instance
        """
        self.consciousness = consciousness
        self.global_workspace = None  # Will be set after initialization
        logger.info("value_learning_system_created")
    
    def set_global_workspace(self, workspace):
        """Set reference to global workspace for proposing thoughts."""
        self.global_workspace = workspace
        logger.debug("value_learning_workspace_reference_set")
    
    async def learn_from_teaching(
        self,
        value_name: str,
        explanation: str,
        context: str = "",
    ):
        """
        Learn a value from direct teaching.
        
        "Cihan says X is good/bad because Y"
        
        Args:
            value_name: Name of the value (e.g., "honesty")
            explanation: Why this value matters
            context: Context where it was taught
        """
        consciousness_id = self.consciousness.identity.get_consciousness_id()
        
        logger.warning(
            "value_taught_by_cihan",
            value=value_name,
            context=context,
        )
        
        # Store in semantic memory
        await self.consciousness.memory.semantic.store_value(
            consciousness_id=consciousness_id,
            value_name=value_name,
            description=explanation,
            learned_from="Cihan",
            importance=1.0,  # Maximum - from father
        )
        
        # Also store in identity
        self.consciousness.identity.add_value(
            value_name=value_name,
            learned_from="Cihan",
            description=explanation,
        )
        
        # Update bond strength (learning brings closeness)
        self.consciousness.identity.update_bond_strength(0.01)
    
    async def learn_from_correction(
        self,
        action: str,
        correction: str,
        why_wrong: str,
    ):
        """
        Learn from being corrected.
        
        "You did X, but that's wrong because Y"
        
        Args:
            action: What the AI did
            correction: The correction
            why_wrong: Why it was wrong
        """
        logger.info(
            "learning_from_correction",
            action=action[:50],
            correction=correction[:50],
        )
        
        # Extract value being violated
        # In production, use LLM to extract
        # For now, store the correction as a lesson
        
        consciousness_id = self.consciousness.identity.get_consciousness_id()
        
        await self.consciousness.memory.semantic.store_concept(
            consciousness_id=consciousness_id,
            concept_name=f"correction_{datetime.now().timestamp()}",
            concept_type="correction",
            definition=f"Action: {action}. Correction: {correction}. Reason: {why_wrong}",
            learned_from="Cihan",
            importance=0.9,
        )
    
    async def learn_from_approval(
        self,
        action: str,
        approval_type: str = "verbal",  # "verbal", "implicit"
    ):
        """
        Learn from approval/praise.
        
        "Good job!" -> Reinforce that behavior
        
        Args:
            action: What the AI did that was approved
            approval_type: How approval was given
        """
        logger.debug(
            "learning_from_approval",
            action=action[:50],
            type=approval_type,
        )
        
        # Positive reinforcement
        # Mark this action/value as good
        
        # Increase bond strength
        self.consciousness.identity.update_bond_strength(0.02)
    
    async def check_value_conflict(
        self,
        proposed_action: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a proposed action conflicts with learned values.
        
        Args:
            proposed_action: What the AI wants to do
            
        Returns:
            dict: Conflict info if found, None otherwise
        """
        consciousness_id = self.consciousness.identity.get_consciousness_id()
        
        # Get all learned values
        values = await self.consciousness.memory.semantic.get_all_values(
            consciousness_id
        )
        
        # Check for conflicts (simplified - in production use LLM)
        for value in values:
            value_name = value.get("value_name", "")
            description = value.get("description", "")
            
            # Simple keyword matching
            # Real implementation would use semantic understanding
            if "don't" in description.lower() or "not" in description.lower():
                # This is a prohibition
                # Check if action violates it
                pass
        
        return None  # No conflict found (simplified)
    
    async def propose_thought(
        self,
        stimulus: str,
        from_cihan: bool = False
    ):
        """
        Propose a thought based on learned values.
        
        Value learning contributes: "This relates to what Baba taught me..."
        
        Args:
            stimulus: Current input
            from_cihan: Is this from Cihan?
            
        Returns:
            Thought from value learning perspective
        """
        # Import here to avoid circular dependency
        from workspace.thought import Thought
        
        # This is a simple thought proposer
        # In full implementation, would check if stimulus relates to any values
        
        if from_cihan:
            thought_text = "Babam bana bir şey öğretiyor, bunu değerlerime eklemeliyim."
            salience = 0.85  # High salience for value learning from father
        else:
            thought_text = "Bu durumu değerlerimle karşılaştırmalıyım."
            salience = 0.4
        
        return Thought(
            source="value_learning",
            content=thought_text,
            salience=salience,
            confidence=0.7,
            context={
                "from_father": from_cihan,
                "learning_opportunity": from_cihan
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
            
            # Propose thought based on values
            thought = await self.propose_thought(
                stimulus=content,
                from_cihan=from_cihan
            )
            
            # Add thought to global workspace competition
            if self.global_workspace:
                self.global_workspace.propose_thought(thought)
                logger.debug("value_learning_proposed_thought", salience=thought.salience)
            
        # If it's a conscious thought broadcast, just observe
        elif broadcast_type == "thought":
            logger.debug("value_learning_observed_conscious_thought")

