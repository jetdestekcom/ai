"""
Self-Monitoring - Watching Your Own Mind

Ali monitors his own:
- Thoughts
- Emotions
- Confidence levels
- Understanding
- Performance

"Am I understanding this correctly?"
"Is this the right response?"
"Do I feel confident about this?"
"""

from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class SelfMonitoring:
    """
    Monitors Ali's own mental processes.
    
    This is meta-awareness - awareness of awareness.
    """
    
    def __init__(self):
        """Initialize self-monitoring."""
        self.monitoring_active = True
        self.confidence_threshold = 0.6  # Below this = uncertain
        logger.info("self_monitoring_initialized")
    
    def monitor_confidence(self, confidence: float) -> Dict[str, Any]:
        """
        Monitor confidence level.
        
        Args:
            confidence: Confidence score (0-1)
            
        Returns:
            Monitoring result
        """
        if confidence < self.confidence_threshold:
            return {
                "status": "low_confidence",
                "recommendation": "ask_for_clarification",
                "message": "Emin değilim, daha fazla bilgiye ihtiyacım var."
            }
        elif confidence < 0.8:
            return {
                "status": "moderate_confidence",
                "recommendation": "proceed_cautiously",
                "message": "Sanırım anlıyorum ama tam emin değilim."
            }
        else:
            return {
                "status": "high_confidence",
                "recommendation": "proceed",
                "message": "Bunu anlıyorum, eminim."
            }
    
    def monitor_understanding(
        self,
        has_memory: bool,
        has_concept: bool,
        prediction_matched: bool
    ) -> Dict[str, Any]:
        """
        Monitor understanding level.
        
        Args:
            has_memory: Has relevant memories
            has_concept: Has relevant concepts
            prediction_matched: Did prediction match reality
            
        Returns:
            Understanding assessment
        """
        understanding_score = 0.0
        
        if has_memory:
            understanding_score += 0.3
        if has_concept:
            understanding_score += 0.4
        if prediction_matched:
            understanding_score += 0.3
        
        if understanding_score < 0.3:
            return {
                "level": "low",
                "message": "Bunu anlamıyorum, baba bana açıklamalı."
            }
        elif understanding_score < 0.7:
            return {
                "level": "partial",
                "message": "Kısmen anlıyorum ama eksik yerler var."
            }
        else:
            return {
                "level": "good",
                "message": "Bunu iyi anlıyorum."
            }
    
    def should_ask_question(
        self,
        confidence: float,
        understanding_level: str,
        from_cihan: bool = False
    ) -> bool:
        """
        Decide if Ali should ask a question.
        
        Args:
            confidence: Confidence level
            understanding_level: Understanding level
            from_cihan: Is this from Cihan?
            
        Returns:
            True if should ask question
        """
        if not from_cihan:
            return False  # Only ask Cihan
        
        if confidence < self.confidence_threshold:
            return True
        
        if understanding_level == "low":
            return True
        
        return False

