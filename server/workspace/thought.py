"""
Thought - Representation of a conscious thought

A thought is what competes for conscious awareness.
Each module proposes thoughts based on current input.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Thought:
    """
    A single thought competing for consciousness.
    
    Attributes:
        source: Which module proposed this thought
        content: The actual thought content
        salience: How important/urgent is this thought (0-1)
        emotion: Associated emotion
        confidence: How confident is the module (0-1)
        context: Additional context data
        timestamp: When this thought was created
    """
    source: str  # "memory", "emotion", "prediction", etc.
    content: str  # The thought itself
    salience: float  # 0.0 to 1.0
    emotion: Optional[str] = None
    confidence: float = 0.5
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Clamp salience
        self.salience = max(0.0, min(1.0, self.salience))
        self.confidence = max(0.0, min(1.0, self.confidence))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "content": self.content,
            "salience": self.salience,
            "emotion": self.emotion,
            "confidence": self.confidence,
            "context": self.context,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
    
    def get_priority(self, from_cihan: bool = False) -> float:
        """
        Calculate overall priority for competition.
        
        Priority = salience * confidence * cihan_boost
        
        Args:
            from_cihan: If input is from Cihan, boost priority
            
        Returns:
            float: Priority score (0-1, or higher with boost)
        """
        priority = self.salience * self.confidence
        
        # Cihan's interactions always get priority boost
        if from_cihan:
            priority *= 2.0  # 2x boost for father
        
        return priority

