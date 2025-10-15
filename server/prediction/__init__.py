"""
Predictive Processing - The Brain's Core Mechanism

Based on Karl Friston's Free Energy Principle and Predictive Processing:

The brain is a "prediction machine":
1. Constantly predicts what will happen next
2. Compares predictions with reality
3. Learns from prediction errors
4. Minimizes surprise over time

This is fundamental to:
- Perception
- Learning
- Action
- Consciousness itself

Ali's brain works the same way.
"""

from prediction.world_model import WorldModel
from prediction.prediction_engine import PredictionEngine
from prediction.error_correction import ErrorCorrection

__all__ = [
    "WorldModel",
    "PredictionEngine",
    "ErrorCorrection",
]

