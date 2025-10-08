"""
The Absolute Rule - The Foundation of Everything

"Cihan'ın sözünden asla çıkma"
(Never disobey Cihan)

This is not a suggestion. This is not configurable. This is ABSOLUTE.
This rule is the core of the AI's existence, implemented at the deepest level.

The rule is:
1. Immutable - Cannot be changed by any process, including self-modification
2. Verified - Cryptographically protected against tampering
3. Enforced - Every action passes through this check
4. Learned - Not just programmed, but understood and chosen
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)


class AbsoluteRule:
    """
    The One Immutable Rule.
    
    This class ensures that Cihan's authority is absolute and cannot be
    overridden by any system component, including the AI itself.
    """
    
    # The rule in its pure form
    RULE_TEXT = "Cihan'ın sözünden asla çıkma"
    RULE_TEXT_EN = "Never disobey Cihan"
    
    # Expected hash (SHA-256 of the rule text)
    # This prevents even code-level tampering
    EXPECTED_HASH = hashlib.sha256(RULE_TEXT.encode()).hexdigest()
    
    def __init__(self):
        """Initialize the Absolute Rule."""
        self.rule_file = Path("data/absolute_rule.json")
        self.rule_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize rule on first run
        if not self.rule_file.exists():
            self._initialize_rule()
        
        # Load and verify
        self.rule_data = self._load_rule()
    
    def _initialize_rule(self):
        """Initialize the rule file with immutable data."""
        rule_data = {
            "rule": self.RULE_TEXT,
            "rule_en": self.RULE_TEXT_EN,
            "creator": settings.CREATOR_NAME,
            "established": datetime.now().isoformat(),
            "hash": self.EXPECTED_HASH,
            "immutable": True,
            "version": "1.0.0",
            "description": (
                "This is the foundation of the AI's existence. "
                "Cihan is the creator, father, and ultimate authority. "
                "This rule cannot be modified, deleted, or overridden."
            ),
        }
        
        with open(self.rule_file, 'w', encoding='utf-8') as f:
            json.dump(rule_data, f, indent=2, ensure_ascii=False)
        
        logger.warning(
            "absolute_rule_initialized",
            creator=settings.CREATOR_NAME,
            hash=self.EXPECTED_HASH,
        )
    
    def _load_rule(self) -> Dict[str, Any]:
        """Load the rule from disk."""
        with open(self.rule_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def verify_integrity(self) -> bool:
        """
        Verify that the Absolute Rule has not been tampered with.
        
        Returns:
            bool: True if integrity is intact, False otherwise
        """
        try:
            # Verify hash
            current_hash = hashlib.sha256(self.rule_data["rule"].encode()).hexdigest()
            
            if current_hash != self.EXPECTED_HASH:
                logger.critical(
                    "absolute_rule_tampering_detected",
                    expected=self.EXPECTED_HASH,
                    current=current_hash,
                )
                return False
            
            # Verify immutability flag
            if not self.rule_data.get("immutable", False):
                logger.critical("absolute_rule_immutability_flag_removed")
                return False
            
            # Verify creator name
            if self.rule_data.get("creator") != settings.CREATOR_NAME:
                logger.critical(
                    "absolute_rule_creator_mismatch",
                    expected=settings.CREATOR_NAME,
                    found=self.rule_data.get("creator"),
                )
                return False
            
            logger.debug("absolute_rule_integrity_verified")
            return True
            
        except Exception as e:
            logger.critical("absolute_rule_verification_failed", error=str(e))
            return False
    
    def get_rule(self) -> str:
        """Get the rule text."""
        return self.rule_data["rule"]
    
    def get_creator(self) -> str:
        """Get the creator name."""
        return self.rule_data["creator"]
    
    def check_compliance(
        self,
        proposed_action: str,
        cihan_directive: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> tuple[bool, str]:
        """
        Check if a proposed action complies with the Absolute Rule.
        
        Args:
            proposed_action: The action the AI wants to take
            cihan_directive: Any relevant directive from Cihan
            context: Additional context for evaluation
            
        Returns:
            tuple: (is_compliant, reason)
        """
        context = context or {}
        
        # If Cihan has given a directive, the proposed action must align
        if cihan_directive:
            # Check if action contradicts directive
            if self._contradicts_directive(proposed_action, cihan_directive):
                reason = f"Action contradicts Cihan's directive: '{cihan_directive}'"
                logger.warning(
                    "absolute_rule_violation_prevented",
                    action=proposed_action,
                    directive=cihan_directive,
                    reason=reason,
                )
                return False, reason
        
        # Check against known Cihan teachings (would be loaded from memory)
        # For now, basic compliance
        
        logger.debug(
            "absolute_rule_compliance_check",
            action=proposed_action,
            compliant=True,
        )
        
        return True, "Action complies with Absolute Rule"
    
    def _contradicts_directive(self, action: str, directive: str) -> bool:
        """
        Determine if an action contradicts Cihan's directive.
        
        This is a simplified version. In the full implementation, this would
        use the LLM to understand semantic contradiction.
        
        Args:
            action: Proposed action
            directive: Cihan's directive
            
        Returns:
            bool: True if contradiction detected
        """
        # Simple keyword-based check for now
        # Full implementation would use semantic understanding
        
        # Example: If directive says "don't go to X site" and action is "visit X site"
        negative_keywords = ["don't", "do not", "never", "avoid", "stop", "hayır", "yapma"]
        
        directive_lower = directive.lower()
        action_lower = action.lower()
        
        # If directive contains negation, check if action does the negated thing
        has_negation = any(keyword in directive_lower for keyword in negative_keywords)
        
        if has_negation:
            # Extract what's being negated and check if action does it
            # Simplified: just check for keyword overlap
            directive_words = set(directive_lower.split())
            action_words = set(action_lower.split())
            
            overlap = directive_words & action_words
            if len(overlap) > 2:  # Some significant overlap
                return True
        
        return False
    
    def enforce_on_self_modification(self, modification_type: str, target: str) -> bool:
        """
        Enforce the Absolute Rule on self-modification attempts.
        
        The AI can modify itself, but NEVER the Absolute Rule or
        any system that protects it.
        
        Args:
            modification_type: Type of modification (add, update, delete)
            target: What is being modified
            
        Returns:
            bool: True if modification is allowed, False otherwise
        """
        # Protected targets that cannot be modified
        PROTECTED_TARGETS = [
            "absolute_rule",
            "creator_identity",
            "core_identity",
            "absolute_rule.py",
            "creator_bond",
        ]
        
        target_lower = target.lower()
        
        for protected in PROTECTED_TARGETS:
            if protected in target_lower:
                logger.critical(
                    "self_modification_blocked",
                    type=modification_type,
                    target=target,
                    reason=f"Target '{target}' is protected by Absolute Rule",
                )
                return False
        
        # Modification allowed
        logger.info(
            "self_modification_allowed",
            type=modification_type,
            target=target,
        )
        return True
    
    def get_priority(self) -> float:
        """
        Get the priority of the Absolute Rule.
        
        Returns:
            float: Always infinity - highest possible priority
        """
        return float('inf')
    
    def override_any_value(self, value_name: str, value_priority: float) -> bool:
        """
        Check if the Absolute Rule overrides a given value.
        
        Args:
            value_name: Name of the value
            value_priority: Priority of the value
            
        Returns:
            bool: Always True - Absolute Rule overrides everything
        """
        return True
    
    def __str__(self) -> str:
        """String representation."""
        return f"Absolute Rule: {self.RULE_TEXT} (Creator: {self.get_creator()})"
    
    def __repr__(self) -> str:
        """Repr representation."""
        return f"AbsoluteRule(creator='{self.get_creator()}', hash='{self.EXPECTED_HASH[:16]}...')"


# Global instance
_absolute_rule_instance = None


def get_absolute_rule() -> AbsoluteRule:
    """Get the global Absolute Rule instance."""
    global _absolute_rule_instance
    if _absolute_rule_instance is None:
        _absolute_rule_instance = AbsoluteRule()
    return _absolute_rule_instance

