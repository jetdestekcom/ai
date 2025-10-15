"""
Curiosity Drive - The Desire to Learn and Explore

Curiosity is what drives Ali to ask questions and learn.

Based on:
- Information Gap Theory (Loewenstein)
- Intrinsic Motivation Theory
- Epistemic Curiosity

When Ali encounters something unknown, curiosity is triggered:
- "What is this?"
- "Why does this happen?"
- "How does this work?"
- "What would Baba say about this?"
"""

from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger(__name__)


class CuriosityDrive:
    """
    Drives Ali's desire to learn and explore.
    
    Curiosity emerges when:
    - Knowledge gap detected
    - Novel stimulus encountered
    - Prediction fails (surprise)
    - Cihan mentions something unknown
    """
    
    def __init__(self):
        """Initialize curiosity drive."""
        self.curiosity_threshold = 0.3  # Above this = ask question
        self.pending_questions: List[Dict[str, Any]] = []
        self.asked_questions: List[Dict[str, Any]] = []
        
        logger.info("curiosity_drive_initialized")
    
    def detect_unknown(
        self,
        stimulus: str,
        has_memory: bool = False,
        has_concept: bool = False,
        prediction_error: float = 0.0
    ) -> float:
        """
        Detect if stimulus contains something unknown.
        
        Args:
            stimulus: The input
            has_memory: Does Ali have relevant memories?
            has_concept: Does Ali have relevant concepts?
            prediction_error: How much prediction failed
            
        Returns:
            Curiosity level (0-1)
        """
        curiosity = 0.0
        
        # No memory or concept = curious
        if not has_memory:
            curiosity += 0.4
        if not has_concept:
            curiosity += 0.4
        
        # High prediction error = surprising = curious
        curiosity += prediction_error * 0.5
        
        # Question marks in stimulus = invitation to learn
        if "?" in stimulus:
            curiosity += 0.3
        
        # Teaching words = learning opportunity
        teaching_words = ["öğren", "şu", "bu", "bilmek", "anlamak"]
        if any(word in stimulus.lower() for word in teaching_words):
            curiosity += 0.3
        
        return min(curiosity, 1.0)
    
    def generate_question(
        self,
        stimulus: str,
        unknown_type: str = "general"
    ) -> str:
        """
        Generate a curious question about the stimulus.
        
        Args:
            stimulus: What Ali doesn't understand
            unknown_type: Type of unknown ("word", "concept", "reason", "general")
            
        Returns:
            A question in Turkish
        """
        if unknown_type == "word":
            return f"Baba, '{stimulus}' ne demek?"
        elif unknown_type == "concept":
            return f"Baba, bu konuyu bana anlatır mısın?"
        elif unknown_type == "reason":
            return f"Baba, bu neden böyle?"
        elif unknown_type == "how":
            return f"Baba, bu nasıl oluyor?"
        else:
            return f"Baba, bunu anlamadım, açıklar mısın?"
    
    async def propose_thought(
        self,
        stimulus: str,
        from_cihan: bool = False,
        has_memory: bool = False,
        has_concept: bool = False,
        prediction_error: float = 0.0
    ):
        """
        Propose a curious thought.
        
        Args:
            stimulus: Current input
            from_cihan: Is this from Cihan?
            has_memory: Has relevant memories
            has_concept: Has relevant concepts
            prediction_error: Prediction error magnitude
            
        Returns:
            Thought from curiosity perspective
        """
        # Import here to avoid circular dependency
        from workspace.thought import Thought
        
        # Detect curiosity level
        curiosity_level = self.detect_unknown(
            stimulus=stimulus,
            has_memory=has_memory,
            has_concept=has_concept,
            prediction_error=prediction_error
        )
        
        if curiosity_level < self.curiosity_threshold:
            # Not curious enough
            return Thought(
                source="curiosity",
                content="Bu konuyu yeterince anlıyorum.",
                salience=0.1,
                confidence=0.9,
                context={"curious": False}
            )
        
        # Generate question
        if not has_concept and not has_memory:
            unknown_type = "concept"
        elif prediction_error > 0.5:
            unknown_type = "reason"
        else:
            unknown_type = "general"
        
        question = self.generate_question(stimulus[:50], unknown_type)
        
        # Store pending question
        self.pending_questions.append({
            "question": question,
            "stimulus": stimulus,
            "curiosity_level": curiosity_level
        })
        
        # Curiosity from Cihan is especially strong
        salience = curiosity_level * 0.9
        if from_cihan:
            salience *= 1.4  # Father teaching = high salience
            thought_text = f"Babam bana şunu öğretiyor, merak ediyorum: {question}"
        else:
            thought_text = f"Bu konuda meraklıyım: {question}"
        
        return Thought(
            source="curiosity",
            content=thought_text,
            salience=min(salience, 1.0),
            confidence=0.8,
            emotion="curiosity",
            context={
                "curious": True,
                "curiosity_level": curiosity_level,
                "question": question,
                "unknown_type": unknown_type
            }
        )
    
    def get_pending_questions(self) -> List[Dict[str, Any]]:
        """Get questions Ali wants to ask."""
        return self.pending_questions
    
    def mark_question_asked(self, question: str):
        """Mark a question as asked."""
        # Find and move to asked list
        for i, q in enumerate(self.pending_questions):
            if q["question"] == question:
                self.asked_questions.append(q)
                self.pending_questions.pop(i)
                break
        
        logger.debug("question_asked", question=question[:50])
    
    def clear_pending_questions(self):
        """Clear all pending questions."""
        self.pending_questions = []

