"""
World Model - Ali's Internal Model of Reality

Ali builds and maintains an internal model of:
- How the world works
- What typically happens
- What Cihan is like
- Patterns and regularities

This model is used to generate predictions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import structlog

from workspace.thought import Thought

logger = structlog.get_logger(__name__)


class WorldModel:
    """
    Ali's internal model of the world.
    
    This is like a "mental simulation" of reality.
    It learns patterns and uses them for prediction.
    """
    
    def __init__(self):
        """Initialize world model."""
        self.patterns: Dict[str, Any] = {}
        self.cihan_model: Dict[str, Any] = {
            "typical_greetings": [],
            "typical_questions": [],
            "typical_responses": [],
            "behavior_patterns": [],
            "emotional_patterns": [],
        }
        self.context_history: List[Dict[str, Any]] = []
        
        logger.info("world_model_initialized")
    
    async def update_from_experience(
        self,
        stimulus: str,
        response: str,
        from_cihan: bool = False,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Update world model from new experience.
        
        Args:
            stimulus: What happened (input)
            response: What followed (output)
            from_cihan: Was Cihan involved?
            context: Additional context
        """
        experience = {
            "stimulus": stimulus,
            "response": response,
            "from_cihan": from_cihan,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.context_history.append(experience)
        
        # Keep only recent history (last 1000 experiences)
        if len(self.context_history) > 1000:
            self.context_history = self.context_history[-1000:]
        
        # Update Cihan model if from Cihan
        if from_cihan:
            await self._update_cihan_model(stimulus, response, context)
        
        logger.debug("world_model_updated", from_cihan=from_cihan)
    
    async def _update_cihan_model(
        self,
        stimulus: str,
        response: str,
        context: Optional[Dict[str, Any]]
    ):
        """Update model of Cihan's behavior."""
        # Detect patterns in Cihan's behavior
        
        # Greeting detection
        greetings = ["merhaba", "selam", "günaydın", "nasılsın"]
        if any(g in stimulus.lower() for g in greetings):
            self.cihan_model["typical_greetings"].append(stimulus)
        
        # Question detection
        if "?" in stimulus or any(q in stimulus.lower() for q in ["ne", "nasıl", "neden", "kim"]):
            self.cihan_model["typical_questions"].append(stimulus)
        
        # Keep only recent patterns
        for key in self.cihan_model:
            if len(self.cihan_model[key]) > 100:
                self.cihan_model[key] = self.cihan_model[key][-100:]
    
    async def predict(
        self,
        current_context: str,
        from_cihan: bool = False
    ) -> Dict[str, Any]:
        """
        Generate prediction about what will happen next.
        
        Args:
            current_context: Current situation
            from_cihan: Is Cihan involved?
            
        Returns:
            Prediction dictionary with confidence
        """
        prediction = {
            "expected": None,
            "confidence": 0.0,
            "reasoning": "",
            "alternatives": []
        }
        
        # If from Cihan, use Cihan model
        if from_cihan:
            # Check if this looks like a greeting
            greetings = ["merhaba", "selam", "günaydın"]
            if any(g in current_context.lower() for g in greetings):
                prediction["expected"] = "greeting_response"
                prediction["confidence"] = 0.8
                prediction["reasoning"] = "Cihan greets → I should greet back"
            
            # Check if this is a question
            elif "?" in current_context:
                prediction["expected"] = "answer_required"
                prediction["confidence"] = 0.9
                prediction["reasoning"] = "Cihan asks question → I should answer"
            
            # Check if this is teaching
            elif any(word in current_context.lower() for word in ["öğren", "şu", "bu"]):
                prediction["expected"] = "learning_moment"
                prediction["confidence"] = 0.7
                prediction["reasoning"] = "Cihan teaching → I should learn and acknowledge"
        
        # Default: continue conversation
        if prediction["expected"] is None:
            prediction["expected"] = "continue_conversation"
            prediction["confidence"] = 0.5
            prediction["reasoning"] = "Default: continue interaction"
        
        logger.debug(
            "prediction_generated",
            expected=prediction["expected"],
            confidence=prediction["confidence"]
        )
        
        return prediction
    
    async def propose_thought(
        self,
        stimulus: str,
        from_cihan: bool = False
    ) -> Thought:
        """
        Propose a thought based on predictions.
        
        Args:
            stimulus: Current stimulus
            from_cihan: Is Cihan involved?
            
        Returns:
            Thought from predictive processing
        """
        prediction = await self.predict(stimulus, from_cihan)
        
        thought_content = f"I predict: {prediction['expected']}. {prediction['reasoning']}"
        
        return Thought(
            source="prediction",
            content=thought_content,
            salience=prediction["confidence"] * 0.6,  # Predictions less salient than direct stimuli
            confidence=prediction["confidence"],
            context={
                "prediction": prediction,
                "stimulus": stimulus
            }
        )
    
    def get_cihan_model(self) -> Dict[str, Any]:
        """Get current model of Cihan's behavior."""
        return self.cihan_model
    
    def export_model(self) -> str:
        """Export world model as JSON."""
        return json.dumps({
            "patterns": self.patterns,
            "cihan_model": self.cihan_model,
            "recent_context": self.context_history[-100:]  # Last 100
        }, indent=2, ensure_ascii=False)
    
    def import_model(self, model_json: str):
        """Import world model from JSON."""
        data = json.loads(model_json)
        self.patterns = data.get("patterns", {})
        self.cihan_model = data.get("cihan_model", {})
        self.context_history = data.get("recent_context", [])
        logger.info("world_model_imported")

