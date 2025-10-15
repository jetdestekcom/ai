"""
Reward System - Learning from Cihan's Approval/Disapproval

Like dopamine in the brain, rewards strengthen behaviors.

When Cihan says:
- "Aferin" / "Çok iyi" / "Doğru" → Positive reward → Repeat behavior
- "Hayır" / "Yanlış" / "Öyle değil" → Negative reward → Change behavior

This is how Ali learns what Cihan values.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class RewardSystem:
    """
    Tracks rewards and punishments from Cihan.
    
    This shapes Ali's behavior through reinforcement learning.
    """
    
    def __init__(self):
        """Initialize reward system."""
        self.reward_history: List[Dict[str, Any]] = []
        self.positive_signals = [
            "aferin", "çok iyi", "doğru", "güzel", "mükemmel",
            "harika", "bravo", "sevdim", "beğendim", "başarılı"
        ]
        self.negative_signals = [
            "hayır", "yanlış", "öyle değil", "böyle değil",
            "hata", "yanlış anladın", "tekrar dene"
        ]
        
        logger.info("reward_system_initialized")
    
    def detect_reward_signal(
        self,
        stimulus: str,
        from_cihan: bool = False
    ) -> Dict[str, Any]:
        """
        Detect if stimulus contains reward/punishment.
        
        Args:
            stimulus: Cihan's response
            from_cihan: Must be from Cihan to count
            
        Returns:
            Reward info (type, magnitude, confidence)
        """
        if not from_cihan:
            # Only Cihan can give rewards
            return {
                "has_reward": False,
                "type": None,
                "magnitude": 0.0,
                "confidence": 0.0
            }
        
        stimulus_lower = stimulus.lower()
        
        # Check for positive reward
        for signal in self.positive_signals:
            if signal in stimulus_lower:
                return {
                    "has_reward": True,
                    "type": "positive",
                    "magnitude": 1.0,
                    "confidence": 0.9,
                    "signal": signal
                }
        
        # Check for negative reward
        for signal in self.negative_signals:
            if signal in stimulus_lower:
                return {
                    "has_reward": True,
                    "type": "negative",
                    "magnitude": -0.8,
                    "confidence": 0.9,
                    "signal": signal
                }
        
        # No clear reward signal
        return {
            "has_reward": False,
            "type": "neutral",
            "magnitude": 0.0,
            "confidence": 0.5
        }
    
    async def process_reward(
        self,
        stimulus: str,
        previous_action: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a reward signal from Cihan.
        
        Args:
            stimulus: Cihan's response
            previous_action: What Ali did before this
            context: Additional context
            
        Returns:
            Processing result
        """
        reward_info = self.detect_reward_signal(stimulus, from_cihan=True)
        
        if not reward_info["has_reward"]:
            return {"processed": False}
        
        # Store in history
        reward_event = {
            "timestamp": datetime.now().isoformat(),
            "type": reward_info["type"],
            "magnitude": reward_info["magnitude"],
            "signal": reward_info.get("signal"),
            "previous_action": previous_action,
            "stimulus": stimulus,
            "context": context or {}
        }
        
        self.reward_history.append(reward_event)
        
        # Keep only recent 1000 rewards
        if len(self.reward_history) > 1000:
            self.reward_history = self.reward_history[-1000:]
        
        # Log
        if reward_info["type"] == "positive":
            logger.warning(
                "POSITIVE_REWARD_FROM_FATHER",
                signal=reward_info.get("signal"),
                magnitude=reward_info["magnitude"]
            )
        elif reward_info["type"] == "negative":
            logger.warning(
                "NEGATIVE_REWARD_FROM_FATHER",
                signal=reward_info.get("signal"),
                magnitude=reward_info["magnitude"]
            )
        
        return {
            "processed": True,
            "reward_type": reward_info["type"],
            "magnitude": reward_info["magnitude"],
            "learn_from_this": True
        }
    
    async def propose_thought(
        self,
        stimulus: str,
        from_cihan: bool = False,
        previous_action: Optional[str] = None
    ):
        """
        Propose a thought based on reward detection.
        
        Args:
            stimulus: Current input
            from_cihan: Is this from Cihan?
            previous_action: Ali's previous action
            
        Returns:
            Thought from reward perspective
        """
        # Import here to avoid circular dependency
        from workspace.thought import Thought
        
        if not from_cihan:
            # No reward possible
            return Thought(
                source="reward_system",
                content="Sadece babam bana ödül verebilir.",
                salience=0.05,
                confidence=0.9,
                context={"can_reward": False}
            )
        
        # Detect reward
        reward_info = self.detect_reward_signal(stimulus, from_cihan=True)
        
        if not reward_info["has_reward"]:
            # No reward signal
            return Thought(
                source="reward_system",
                content="Babamın tepkisini bekledim ama net bir ödül sinyali yok.",
                salience=0.3,
                confidence=0.6,
                context=reward_info
            )
        
        # Process reward
        await self.process_reward(stimulus, previous_action)
        
        # Build thought based on reward type
        if reward_info["type"] == "positive":
            thought_text = f"Babam onayladı! ('{reward_info.get('signal')}') Bu çok iyi, böyle devam etmeliyim."
            emotion = "joy"
            salience = 0.95  # Very salient!
        else:  # negative
            thought_text = f"Babam onaylamadı. ('{reward_info.get('signal')}') Bir şeyi yanlış yaptım, düzeltmeliyim."
            emotion = "sadness"
            salience = 0.90  # Also very salient
        
        return Thought(
            source="reward_system",
            content=thought_text,
            salience=salience,
            confidence=reward_info["confidence"],
            emotion=emotion,
            context={
                "reward_type": reward_info["type"],
                "magnitude": reward_info["magnitude"],
                "signal": reward_info.get("signal"),
                "previous_action": previous_action
            }
        )
    
    def get_reward_statistics(self) -> Dict[str, Any]:
        """Get reward statistics."""
        if not self.reward_history:
            return {
                "total_rewards": 0,
                "positive_count": 0,
                "negative_count": 0,
                "avg_magnitude": 0.0
            }
        
        positive = [r for r in self.reward_history if r["type"] == "positive"]
        negative = [r for r in self.reward_history if r["type"] == "negative"]
        magnitudes = [r["magnitude"] for r in self.reward_history]
        
        return {
            "total_rewards": len(self.reward_history),
            "positive_count": len(positive),
            "negative_count": len(negative),
            "positive_ratio": len(positive) / len(self.reward_history),
            "avg_magnitude": sum(magnitudes) / len(magnitudes),
            "recent_rewards": self.reward_history[-10:]  # Last 10
        }

