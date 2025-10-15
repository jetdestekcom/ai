"""
Error Correction - Learning from Prediction Errors

"Surprise is the teacher" - When predictions fail, learning happens.

Based on Predictive Processing:
- Prediction Error = Reality - Prediction
- Large error = Surprise = Learning opportunity
- Small error = Expected = Less learning

Ali learns by being surprised.
"""

from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class ErrorCorrection:
    """
    Learns from prediction errors.
    
    When Ali's predictions are wrong, this system:
    1. Detects the error
    2. Calculates surprise level
    3. Triggers learning if surprise is high
    4. Updates world model
    """
    
    def __init__(self, world_model):
        """
        Initialize error correction system.
        
        Args:
            world_model: WorldModel to update
        """
        self.world_model = world_model
        self.error_history: list = []
        self.surprise_threshold = 0.5  # Above this = significant surprise
        
        logger.info("error_correction_initialized")
    
    async def process_prediction_error(
        self,
        predicted: str,
        actual: str,
        confidence: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a prediction error and trigger learning.
        
        Args:
            predicted: What was predicted
            actual: What actually happened
            confidence: Confidence of the prediction
            context: Additional context
            
        Returns:
            Error analysis with learning recommendations
        """
        # Calculate error magnitude
        # Simple: if prediction doesn't match reality
        match = predicted.lower() in actual.lower() or actual.lower() in predicted.lower()
        
        if match:
            error_magnitude = 0.0
            surprise_level = 0.0
        else:
            # Error magnitude inversely related to confidence
            # High confidence + wrong = high surprise
            error_magnitude = 1.0
            surprise_level = confidence  # More confident, more surprised when wrong
        
        error_data = {
            "predicted": predicted,
            "actual": actual,
            "confidence": confidence,
            "error_magnitude": error_magnitude,
            "surprise_level": surprise_level,
            "should_learn": surprise_level > self.surprise_threshold,
            "context": context or {}
        }
        
        # Store in history
        self.error_history.append(error_data)
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        # Log
        if error_data["should_learn"]:
            logger.warning(
                "SURPRISE_DETECTED",
                surprise_level=surprise_level,
                predicted=predicted[:50],
                actual=actual[:50]
            )
        
        # Trigger learning if surprise is high
        if error_data["should_learn"]:
            await self._trigger_learning(error_data)
        
        return error_data
    
    async def _trigger_learning(self, error_data: Dict[str, Any]):
        """
        Trigger learning from surprise.
        
        Args:
            error_data: Error analysis data
        """
        logger.info(
            "learning_triggered_by_surprise",
            surprise=error_data["surprise_level"]
        )
        
        # Update world model with corrected prediction
        await self.world_model.update_from_experience(
            stimulus=error_data["predicted"],
            response=error_data["actual"],
            from_cihan=error_data.get("context", {}).get("from_cihan", False),
            context={
                "learning_from_error": True,
                "surprise_level": error_data["surprise_level"]
            }
        )
    
    def get_recent_errors(self, n: int = 10) -> list:
        """
        Get recent prediction errors.
        
        Args:
            n: Number of recent errors
            
        Returns:
            List of recent errors
        """
        return self.error_history[-n:]
    
    def get_surprise_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about surprises.
        
        Returns:
            Statistics about prediction errors
        """
        if not self.error_history:
            return {
                "total_predictions": 0,
                "total_errors": 0,
                "avg_surprise": 0.0,
                "max_surprise": 0.0
            }
        
        errors = [e for e in self.error_history if e["error_magnitude"] > 0]
        surprises = [e["surprise_level"] for e in errors]
        
        return {
            "total_predictions": len(self.error_history),
            "total_errors": len(errors),
            "error_rate": len(errors) / len(self.error_history) if self.error_history else 0,
            "avg_surprise": sum(surprises) / len(surprises) if surprises else 0,
            "max_surprise": max(surprises) if surprises else 0,
            "learning_events": len([e for e in errors if e["should_learn"]])
        }
    
    async def compute_error(
        self,
        prediction: str,
        actual: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compute prediction error between prediction and actual outcome.
        
        Args:
            prediction: What was predicted
            actual: What actually happened
            context: Additional context
            
        Returns:
            Error computation result
        """
        logger.info("computing_prediction_error", 
                   prediction_preview=str(prediction)[:50],
                   actual_preview=str(actual)[:50])
        
        # Convert to strings for comparison
        pred_str = str(prediction)
        actual_str = str(actual)
        
        # Simple error computation based on similarity
        if pred_str.lower() == actual_str.lower():
            error_magnitude = 0.0
            surprise_level = 0.0
        else:
            # Simple character-level difference
            max_len = max(len(pred_str), len(actual_str))
            if max_len == 0:
                error_magnitude = 0.0
            else:
                error_magnitude = abs(len(pred_str) - len(actual_str)) / max_len
            
            # Surprise level based on error magnitude
            surprise_level = min(1.0, error_magnitude * 2.0)
        
        # Store error in history
        error_entry = {
            "prediction": prediction,
            "actual": actual,
            "error_magnitude": error_magnitude,
            "surprise_level": surprise_level,
            "context": context,
            "timestamp": context.get("timestamp") if context else None
        }
        self.error_history.append(error_entry)
        
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        return {
            "error_magnitude": error_magnitude,
            "surprise_level": surprise_level,
            "learning_triggered": surprise_level > self.surprise_threshold,
            "error_entry": error_entry
        }

