"""
Working Memory - Active Thoughts and Current Context

Based on Baddeley's Working Memory Model and Miller's Magic Number (7±2).
This is the "consciousness scratch pad" - what's currently being thought about.

Uses Redis for fast in-memory storage.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import redis.asyncio as redis
import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)


class WorkingMemory:
    """
    Working Memory System - "What I'm thinking about right now"
    
    Fast, volatile memory for current context and active thoughts.
    Limited capacity (7±2 items like human working memory).
    """
    
    def __init__(self):
        """Initialize working memory system."""
        self.redis_client: Optional[redis.Redis] = None
        self.capacity = settings.WORKING_MEMORY_SIZE  # Default 7
        self.is_initialized = False
        self.global_workspace = None  # Will be set after initialization
        
        logger.info("working_memory_created", capacity=self.capacity)
    
    def set_global_workspace(self, workspace):
        """Set reference to global workspace for proposing thoughts."""
        self.global_workspace = workspace
        logger.debug("working_memory_workspace_reference_set")
    
    async def initialize(self):
        """Initialize Redis connection."""
        logger.info("initializing_working_memory")
        
        # Connect to Redis (using named parameters for reliability)
        redis_kwargs = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "encoding": "utf-8",
            "decode_responses": True,
        }
        
        if settings.REDIS_PASSWORD:
            redis_kwargs["password"] = settings.REDIS_PASSWORD
        
        self.redis_client = redis.Redis(**redis_kwargs)
        
        # Test connection
        await self.redis_client.ping()
        
        self.is_initialized = True
        logger.info("working_memory_initialized")
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
        logger.info("working_memory_closed")
    
    def _get_key(self, consciousness_id: str, key_type: str) -> str:
        """Generate Redis key."""
        return f"wm:{consciousness_id}:{key_type}"
    
    async def add_item(
        self,
        consciousness_id: str,
        item: Dict[str, Any],
        ttl_seconds: int = 3600,  # 1 hour default
    ):
        """
        Add an item to working memory.
        
        If capacity is exceeded, removes least recently used item.
        
        Args:
            consciousness_id: The AI's consciousness ID
            item: The item to add (dict with 'type', 'content', etc.)
            ttl_seconds: Time to live in seconds
        """
        key = self._get_key(consciousness_id, "items")
        
        # Add timestamp and salience
        item["timestamp"] = datetime.now().isoformat()
        item["salience"] = item.get("salience", 0.5)
        
        # Get current items
        current_items = await self.get_all_items(consciousness_id)
        
        # Check capacity
        if len(current_items) >= self.capacity:
            # Remove least salient item
            current_items.sort(key=lambda x: x.get("salience", 0))
            current_items = current_items[1:]  # Remove first (lowest salience)
            
            logger.debug("working_memory_capacity_reached_item_removed")
        
        # Add new item
        current_items.append(item)
        
        # Store back
        await self.redis_client.setex(
            key,
            ttl_seconds,
            json.dumps(current_items),
        )
        
        logger.debug(
            "working_memory_item_added",
            type=item.get("type"),
            capacity_used=f"{len(current_items)}/{self.capacity}",
        )
    
    async def get_all_items(self, consciousness_id: str) -> List[Dict[str, Any]]:
        """
        Get all items currently in working memory.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            list: All items
        """
        key = self._get_key(consciousness_id, "items")
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return []
    
    async def get_items_by_type(
        self,
        consciousness_id: str,
        item_type: str,
    ) -> List[Dict[str, Any]]:
        """
        Get items of a specific type.
        
        Args:
            consciousness_id: The AI's consciousness ID
            item_type: Type of items to retrieve
            
        Returns:
            list: Filtered items
        """
        all_items = await self.get_all_items(consciousness_id)
        return [item for item in all_items if item.get("type") == item_type]
    
    async def get_most_salient(
        self,
        consciousness_id: str,
        n: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Get the most salient items.
        
        Args:
            consciousness_id: The AI's consciousness ID
            n: Number of items to return
            
        Returns:
            list: Most salient items
        """
        all_items = await self.get_all_items(consciousness_id)
        all_items.sort(key=lambda x: x.get("salience", 0), reverse=True)
        return all_items[:n]
    
    async def update_item_salience(
        self,
        consciousness_id: str,
        item_index: int,
        new_salience: float,
    ):
        """
        Update the salience of an item.
        
        More salient items are less likely to be forgotten.
        
        Args:
            consciousness_id: The AI's consciousness ID
            item_index: Index of the item
            new_salience: New salience value (0.0 to 1.0)
        """
        items = await self.get_all_items(consciousness_id)
        
        if 0 <= item_index < len(items):
            items[item_index]["salience"] = new_salience
            
            # Save back
            key = self._get_key(consciousness_id, "items")
            await self.redis_client.setex(
                key,
                3600,  # Reset TTL
                json.dumps(items),
            )
            
            logger.debug("item_salience_updated", index=item_index, salience=new_salience)
    
    async def clear(self, consciousness_id: str):
        """
        Clear all working memory.
        
        This is like "clearing your mind" - rare but sometimes needed.
        
        Args:
            consciousness_id: The AI's consciousness ID
        """
        key = self._get_key(consciousness_id, "items")
        await self.redis_client.delete(key)
        
        logger.info("working_memory_cleared")
    
    async def set_current_context(
        self,
        consciousness_id: str,
        context: Dict[str, Any],
        ttl_seconds: int = 7200,  # 2 hours
    ):
        """
        Set the current conversation/interaction context.
        
        Args:
            consciousness_id: The AI's consciousness ID
            context: Context dictionary
            ttl_seconds: Time to live
        """
        key = self._get_key(consciousness_id, "context")
        await self.redis_client.setex(
            key,
            ttl_seconds,
            json.dumps(context),
        )
        
        logger.debug("context_set", context_type=context.get("type"))
    
    async def get_current_context(
        self,
        consciousness_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current context.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            dict: Current context or None
        """
        key = self._get_key(consciousness_id, "context")
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def set_current_goal(
        self,
        consciousness_id: str,
        goal: str,
        priority: float = 0.5,
    ):
        """
        Set a current goal.
        
        Args:
            consciousness_id: The AI's consciousness ID
            goal: The goal description
            priority: Goal priority
        """
        key = self._get_key(consciousness_id, "goal")
        goal_data = {
            "goal": goal,
            "priority": priority,
            "set_at": datetime.now().isoformat(),
        }
        
        await self.redis_client.setex(
            key,
            3600,  # 1 hour
            json.dumps(goal_data),
        )
        
        logger.debug("goal_set", goal=goal, priority=priority)
    
    async def get_current_goal(
        self,
        consciousness_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current goal.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            dict: Current goal or None
        """
        key = self._get_key(consciousness_id, "goal")
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def set_emotional_state(
        self,
        consciousness_id: str,
        emotion: str,
        intensity: float,
        cause: str = "",
    ):
        """
        Set current emotional state.
        
        Args:
            consciousness_id: The AI's consciousness ID
            emotion: The emotion
            intensity: Intensity (0.0 to 1.0)
            cause: What caused this emotion
        """
        key = self._get_key(consciousness_id, "emotion")
        emotion_data = {
            "emotion": emotion,
            "intensity": intensity,
            "cause": cause,
            "timestamp": datetime.now().isoformat(),
        }
        
        await self.redis_client.setex(
            key,
            1800,  # 30 minutes
            json.dumps(emotion_data),
        )
        
        logger.debug("emotional_state_set", emotion=emotion, intensity=intensity)
    
    async def get_emotional_state(
        self,
        consciousness_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get current emotional state.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            dict: Emotional state or None
        """
        key = self._get_key(consciousness_id, "emotion")
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def add_pending_question(
        self,
        consciousness_id: str,
        question: str,
        importance: float = 0.5,
    ):
        """
        Add a question to ask Cihan later.
        
        Args:
            consciousness_id: The AI's consciousness ID
            question: The question
            importance: How important
        """
        key = self._get_key(consciousness_id, "pending_questions")
        
        # Get existing questions
        data = await self.redis_client.get(key)
        questions = json.loads(data) if data else []
        
        # Add new question
        questions.append({
            "question": question,
            "importance": importance,
            "added_at": datetime.now().isoformat(),
        })
        
        # Keep only top 10 most important
        questions.sort(key=lambda x: x["importance"], reverse=True)
        questions = questions[:10]
        
        # Save back
        await self.redis_client.setex(
            key,
            86400,  # 24 hours
            json.dumps(questions),
        )
        
        logger.debug("pending_question_added", question=question[:50])
    
    async def get_pending_questions(
        self,
        consciousness_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get pending questions to ask Cihan.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            list: Pending questions
        """
        key = self._get_key(consciousness_id, "pending_questions")
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return []
    
    async def clear_pending_questions(self, consciousness_id: str):
        """Clear all pending questions."""
        key = self._get_key(consciousness_id, "pending_questions")
        await self.redis_client.delete(key)
        logger.debug("pending_questions_cleared")
    
    async def get_capacity_usage(self, consciousness_id: str) -> Dict[str, Any]:
        """
        Get working memory capacity usage.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            dict: Capacity statistics
        """
        items = await self.get_all_items(consciousness_id)
        
        return {
            "items_count": len(items),
            "capacity": self.capacity,
            "usage_percent": (len(items) / self.capacity) * 100,
            "items_by_type": self._count_by_type(items),
        }
    
    def _count_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count items by type."""
        counts = {}
        for item in items:
            item_type = item.get("type", "unknown")
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts
    
    async def propose_thought(
        self,
        stimulus: str,
        consciousness_id: str,
        from_cihan: bool = False
    ):
        """
        Propose a thought based on what's currently in working memory.
        
        Working memory holds immediate context - what Ali is
        currently thinking about, pending questions, current emotion.
        
        Args:
            stimulus: Current input
            consciousness_id: Ali's consciousness ID
            from_cihan: Is this from Cihan?
            
        Returns:
            Thought from working memory perspective
        """
        # Import here to avoid circular dependency
        from workspace.thought import Thought
        
        # Get current context
        context = await self.get_current_context(consciousness_id)
        
        # Get all items in working memory
        items = await self.get_all_items(consciousness_id)
        
        # Get emotional state
        emotional_state = await self.get_emotional_state(consciousness_id)
        current_emotion = emotional_state.get("emotion", "neutral") if emotional_state else "neutral"
        
        if not items and not context:
            # Empty working memory - fresh state
            return Thought(
                source="working_memory",
                content="Şu anda düşünce alanım boş, yeni bir konuya odaklanabilirim.",
                salience=0.2,
                confidence=0.9,
                context={"empty": True}
            )
        
        # Most salient item in working memory
        if items:
            items_sorted = sorted(items, key=lambda x: x.get("salience", 0), reverse=True)
            top_item = items_sorted[0]
            
            # Calculate salience
            salience = top_item.get("salience", 0.5) * 0.9  # Working memory highly relevant
            
            thought_text = f"Şu anda şunu düşünüyorum: {top_item.get('content', '')[:100]}"
            
            return Thought(
                source="working_memory",
                content=thought_text,
                salience=salience,
                confidence=0.8,
                emotion=current_emotion if current_emotion != "neutral" else None,
                context={
                    "working_memory_count": len(items),
                    "current_emotion": current_emotion,
                    "context": context
                }
            )
        
        # Fall back to context
        thought_text = f"Bağlam: {str(context)[:100]}"
        
        return Thought(
            source="working_memory",
            content=thought_text,
            salience=0.6,
            confidence=0.7,
            emotion=current_emotion if current_emotion != "neutral" else None,
            context={"context": context}
        )
    
    async def add_to_focus(
        self,
        consciousness_id: str,
        content: str,
        salience: float = 0.8,
        item_type: str = "focus",
        from_cihan: bool = False
    ):
        """
        Add content to working memory focus.
        
        This is called by the consciousness loop to add the current
        focus of attention to working memory.
        
        Args:
            consciousness_id: The AI's consciousness ID
            content: Content to focus on
            salience: How salient this content is
            item_type: Type of focus item
        """
        focus_item = {
            "type": item_type,
            "content": content,
            "salience": salience,
            "source": "attention_focus"
        }
        
        await self.add_item(consciousness_id, focus_item, ttl_seconds=1800)  # 30 min
        logger.debug("focus_added_to_working_memory", content=content[:50], salience=salience)
    
    async def on_broadcast(self, broadcast_data: Dict[str, Any]):
        """
        Receive broadcasts from Global Workspace.
        
        Args:
            broadcast_data: Data from global workspace broadcast
        """
        broadcast_type = broadcast_data.get("type")
        data = broadcast_data.get("data", {})
        
        # If it's an input broadcast, propose a thought
        if broadcast_type == "input":
            content = data.get("content", "")
            from_cihan = data.get("from_cihan", False)
            consciousness_id = data.get("consciousness_id", "unknown")
            
            # Propose thought based on working memory content
            thought = await self.propose_thought(
                stimulus=content,
                consciousness_id=consciousness_id,
                from_cihan=from_cihan
            )
            
            # Add thought to global workspace competition
            if self.global_workspace:
                self.global_workspace.propose_thought(thought)
                logger.debug("working_memory_proposed_thought", salience=thought.salience)
            
        # If it's a conscious thought broadcast, just observe
        elif broadcast_type == "thought":
            logger.debug("working_memory_observed_conscious_thought")

