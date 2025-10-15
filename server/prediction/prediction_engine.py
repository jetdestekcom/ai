"""
Prediction Engine - Generates Predictions from World Model

The brain constantly predicts what will happen next.
This engine uses the world model to generate those predictions.
"""

from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class PredictionEngine:
    """
    Generates predictions about what will happen.
    
    Uses world model and current context to predict:
    - What Cihan will say next
    - What will happen after an action
    - What response is expected
    """
    
    def __init__(self, world_model):
        """
        Initialize prediction engine.
        
        Args:
            world_model: WorldModel instance
        """
        self.world_model = world_model
        self.active_predictions: Dict[str, Any] = {}
        
        logger.info("prediction_engine_initialized")
    
    async def predict_next(
        self,
        current_state: Dict[str, Any],
        from_cihan: bool = False
    ) -> Dict[str, Any]:
        """
        Predict what will happen next.
        
        Args:
            current_state: Current situation/context
            from_cihan: Is Cihan involved?
            
        Returns:
            Prediction with confidence and alternatives
        """
        context = current_state.get("content", "")
        
        prediction = await self.world_model.predict(
            current_context=context,
            from_cihan=from_cihan
        )
        
        # Store as active prediction
        prediction_id = f"pred_{len(self.active_predictions)}"
        self.active_predictions[prediction_id] = {
            "prediction": prediction,
            "context": current_state,
            "verified": False
        }
        
        return prediction
    
    async def verify_prediction(
        self,
        prediction_id: str,
        actual_outcome: str
    ) -> Dict[str, Any]:
        """
        Verify if prediction was correct.
        
        Args:
            prediction_id: ID of prediction to verify
            actual_outcome: What actually happened
            
        Returns:
            Verification result with error info
        """
        if prediction_id not in self.active_predictions:
            logger.warning("prediction_not_found", id=prediction_id)
            return {"error": "prediction not found"}
        
        pred_data = self.active_predictions[prediction_id]
        prediction = pred_data["prediction"]
        expected = prediction["expected"]
        
        # Simple match check
        match = expected.lower() in actual_outcome.lower()
        
        pred_data["verified"] = True
        pred_data["actual"] = actual_outcome
        pred_data["match"] = match
        
        result = {
            "prediction_id": prediction_id,
            "expected": expected,
            "actual": actual_outcome,
            "match": match,
            "confidence": prediction["confidence"],
            "surprise_level": 0.0 if match else (1.0 - prediction["confidence"])
        }
        
        logger.info(
            "prediction_verified",
            match=match,
            surprise=result["surprise_level"]
        )
        
        return result
    
    def get_active_predictions(self) -> Dict[str, Any]:
        """Get all active predictions."""
        return self.active_predictions
    
    def clear_predictions(self):
        """Clear old predictions."""
        # Keep only unverified predictions
        self.active_predictions = {
            k: v for k, v in self.active_predictions.items()
            if not v.get("verified", False)
        }
        logger.debug("predictions_cleared")

