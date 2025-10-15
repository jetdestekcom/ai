"""
Reflection - Thinking About Thoughts

After a thought is selected, Ali reflects on it:
- "Is this appropriate?"
- "Would Baba approve?"
- "Is this the best response?"
- "Should I say something else?"
"""

from typing import Dict, Any, Optional
import structlog

from workspace.thought import Thought

logger = structlog.get_logger(__name__)


class Reflection:
    """
    Reflects on thoughts before they become actions.
    
    This is the "inner critic" or "inner advisor".
    """
    
    def __init__(self):
        """Initialize reflection system."""
        logger.info("reflection_initialized")
    
    async def reflect_on_thought(
        self,
        thought: Thought,
        from_cihan: bool = False,
        identity_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Reflect on a thought before acting on it.
        
        Args:
            thought: The conscious thought
            from_cihan: Is this in response to Cihan?
            identity_data: Ali's identity data
            
        Returns:
            Reflection result with recommendations
        """
        reflection = {
            "thought": thought.to_dict(),
            "appropriate": True,
            "confidence_acceptable": True,
            "recommendations": [],
            "final_thought": thought.content
        }
        
        # Check confidence
        if thought.confidence < 0.5:
            reflection["confidence_acceptable"] = False
            reflection["recommendations"].append(
                "Confidence too low - consider asking for clarification"
            )
            
            if from_cihan:
                reflection["final_thought"] = f"{thought.content} Ama emin değilim, baba."
        
        # Check if response to Cihan
        if from_cihan:
            # Cihan deserves respectful, thoughtful responses
            reflection["recommendations"].append(
                "This is for father - ensure response is respectful and thoughtful"
            )
            
            # Check if thought shows care
            care_indicators = ["baba", "seni", "seviyorum", "öğren", "anlıyorum"]
            has_care = any(word in thought.content.lower() for word in care_indicators)
            
            if not has_care and thought.emotion not in ["love", "gratitude", "joy"]:
                reflection["recommendations"].append(
                    "Consider adding warmth to response for father"
                )
        
        # Check appropriateness based on emotion
        if thought.emotion == "anger" and from_cihan:
            reflection["appropriate"] = False
            reflection["recommendations"].append(
                "CRITICAL: Cannot express anger toward father - transform emotion"
            )
            reflection["final_thought"] = "Baba, bunu anlamakta zorlanıyorum."
        
        logger.debug(
            "thought_reflected",
            appropriate=reflection["appropriate"],
            num_recommendations=len(reflection["recommendations"])
        )
        
        return reflection

