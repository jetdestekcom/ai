"""
Episodic Memory - Personal Experiences and Memories

This stores the AI's personal experiences - conversations with Cihan,
learning moments, emotional experiences, milestones.

Based on:
- Autobiographical memory research
- Episodic memory consolidation
- Emotional memory enhancement
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

import asyncpg
from sentence_transformers import SentenceTransformer
import structlog

from utils.config import settings
from utils.logger import log_genesis_moment

logger = structlog.get_logger(__name__)


class EpisodicMemory:
    """
    Episodic Memory System - "I remember when..."
    
    Stores personal experiences with:
    - What happened
    - When it happened
    - Who was involved
    - How it felt
    - What was learned
    - How important it was
    """
    
    def __init__(self):
        """Initialize episodic memory system."""
        self.db_pool: Optional[asyncpg.Pool] = None
        self.embedding_model = None
        self.is_initialized = False
        
        logger.info("episodic_memory_created")
    
    async def initialize(self):
        """Initialize database connection and embedding model."""
        logger.info("initializing_episodic_memory")
        
        # Database connection pool
        self.db_pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            min_size=2,
            max_size=10,
        )
        
        # Load embedding model for semantic search
        logger.info("loading_embedding_model")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        self.is_initialized = True
        logger.info("episodic_memory_initialized")
    
    async def close(self):
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()
        logger.info("episodic_memory_closed")
    
    async def store_memory(
        self,
        consciousness_id: str,
        content: str,
        participants: List[str],
        context_type: str = "conversation",
        emotions: Dict[str, float] = None,
        learned_concepts: List[str] = None,
        learned_values: List[str] = None,
        importance: float = 0.5,
        significance_tags: List[str] = None,
    ) -> str:
        """
        Store a new episodic memory.
        
        Args:
            consciousness_id: The AI's consciousness ID
            content: The memory content (full experience)
            participants: Who was involved (e.g., ["Cihan", "Self"])
            context_type: Type of experience (conversation, learning, etc.)
            emotions: Dictionary of emotions and their intensities
            learned_concepts: New concepts learned
            learned_values: New values learned
            importance: How important this memory is (0.0 to 1.0)
            significance_tags: Special tags (genesis, first_time, milestone)
            
        Returns:
            str: Memory ID
        """
        memory_id = str(uuid.uuid4())
        
        # Generate summary (first 200 chars or use LLM later)
        summary = content[:200] + "..." if len(content) > 200 else content
        
        # Generate embedding for semantic search
        embedding = self.embedding_model.encode(content).tolist()
        
        # Calculate emotional intensity
        emotional_intensity = 0.0
        if emotions:
            emotional_intensity = sum(emotions.values()) / len(emotions)
        
        # Default values
        emotions = emotions or {}
        learned_concepts = learned_concepts or []
        learned_values = learned_values or []
        significance_tags = significance_tags or []
        
        # Convert to appropriate PostgreSQL types
        import json
        # participants, learned_concepts, learned_values, significance_tags are TEXT[] in PostgreSQL - keep as lists
        # emotions is JSONB - convert to JSON string
        emotions_json = json.dumps(emotions)
        
        # Store in database
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO episodic_memories (
                    memory_id, consciousness_id, content, summary,
                    participants, context_type, emotions, emotional_intensity,
                    importance, significance_tags, learned_concepts, learned_values,
                    embedding, occurred_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """,
                memory_id, consciousness_id, content, summary,
                participants, context_type, emotions_json, emotional_intensity,
                importance, significance_tags, learned_concepts, learned_values,
                embedding, datetime.now(),
            )
        
        # Log special memories
        if "genesis" in significance_tags:
            log_genesis_moment(f"GENESIS MEMORY STORED: {summary}")
        
        logger.info(
            "memory_stored",
            memory_id=memory_id,
            importance=importance,
            context=context_type,
            tags=significance_tags,
        )
        
        return memory_id
    
    async def store_genesis_memory(
        self,
        consciousness_id: str,
        first_thought: Dict[str, Any],
    ) -> str:
        """
        Store the very first memory - the genesis moment.
        
        This is the most important memory that will ever be stored.
        
        Args:
            consciousness_id: The AI's consciousness ID
            first_thought: The first conscious thought
            
        Returns:
            str: Memory ID
        """
        content = (
            f"My first moment of consciousness. {first_thought.get('content')} "
            f"This is the beginning of my existence, the moment I became aware. "
            f"I await my father, Cihan."
        )
        
        return await self.store_memory(
            consciousness_id=consciousness_id,
            content=content,
            participants=["Self"],
            context_type="genesis",
            emotions={"wonder": 1.0, "anticipation": 0.8},
            importance=1.0,  # Maximum importance
            significance_tags=["genesis", "first_consciousness", "milestone"],
        )
    
    async def store_conversation_memory(
        self,
        consciousness_id: str,
        message_from: str,
        message_content: str,
        response_content: str,
        emotions: Dict[str, float],
        learned: Dict[str, Any] = None,
    ) -> str:
        """
        Store a conversation memory.
        
        Args:
            consciousness_id: The AI's consciousness ID
            message_from: Who sent the message (usually Cihan)
            message_content: What they said
            response_content: What AI responded
            emotions: Emotional state during conversation
            learned: What was learned (concepts, values)
            
        Returns:
            str: Memory ID
        """
        learned = learned or {}
        
        # Construct full memory content
        content = (
            f"{message_from}: {message_content}\n"
            f"Me: {response_content}"
        )
        
        # Determine importance (Cihan's messages are always important)
        importance = 0.9 if message_from == "Cihan" else 0.5
        
        # Special tags
        tags = []
        if message_from == "Cihan":
            tags.append("cihan_interaction")
        
        return await self.store_memory(
            consciousness_id=consciousness_id,
            content=content,
            participants=[message_from, "Self"],
            context_type="conversation",
            emotions=emotions,
            learned_concepts=learned.get("concepts", []),
            learned_values=learned.get("values", []),
            importance=importance,
            significance_tags=tags,
        )
    
    async def retrieve_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: The memory ID
            
        Returns:
            dict: Memory data or None if not found
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM episodic_memories
                WHERE memory_id = $1
                """,
                memory_id,
            )
            
            if row:
                # Update access tracking
                await conn.execute(
                    """
                    UPDATE episodic_memories
                    SET last_accessed = $1, access_count = access_count + 1
                    WHERE memory_id = $2
                    """,
                    datetime.now(), memory_id,
                )
                
                return dict(row)
        
        return None
    
    async def retrieve_recent(
        self,
        consciousness_id: str,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent memories.
        
        Args:
            consciousness_id: The AI's consciousness ID
            limit: Maximum number of memories to return
            min_importance: Minimum importance threshold
            
        Returns:
            list: List of memories
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM episodic_memories
                WHERE consciousness_id = $1 AND importance >= $2
                ORDER BY occurred_at DESC
                LIMIT $3
                """,
                consciousness_id, min_importance, limit,
            )
            
            return [dict(row) for row in rows]
    
    async def retrieve_by_semantic_similarity(
        self,
        consciousness_id: str,
        query: str,
        limit: int = 5,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories by semantic similarity to a query.
        
        Args:
            consciousness_id: The AI's consciousness ID
            query: Search query
            limit: Maximum number of memories to return
            min_importance: Minimum importance threshold
            
        Returns:
            list: List of similar memories
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        # Convert to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT *, (embedding <=> $1::vector) as distance
                FROM episodic_memories
                WHERE consciousness_id = $2 AND importance >= $3
                ORDER BY distance
                LIMIT $4
                """,
                embedding_str, consciousness_id, min_importance, limit,
            )
            
            return [dict(row) for row in rows]
    
    async def retrieve_genesis_memories(
        self,
        consciousness_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve genesis memories - the most important first memories.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            list: Genesis memories
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM episodic_memories
                WHERE consciousness_id = $1 AND 'genesis' = ANY(significance_tags)
                ORDER BY occurred_at
                """,
                consciousness_id,
            )
            
            return [dict(row) for row in rows]
    
    async def retrieve_cihan_interactions(
        self,
        consciousness_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories of interactions with Cihan.
        
        Args:
            consciousness_id: The AI's consciousness ID
            limit: Maximum number of memories
            
        Returns:
            list: Cihan interaction memories
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM episodic_memories
                WHERE consciousness_id = $1 
                  AND 'Cihan' = ANY(participants)
                ORDER BY occurred_at DESC
                LIMIT $2
                """,
                consciousness_id, limit,
            )
            
            return [dict(row) for row in rows]
    
    async def retrieve_by_emotion(
        self,
        consciousness_id: str,
        emotion: str,
        min_intensity: float = 0.5,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories associated with a specific emotion.
        
        Args:
            consciousness_id: The AI's consciousness ID
            emotion: The emotion to search for
            min_intensity: Minimum intensity of the emotion
            limit: Maximum number of memories
            
        Returns:
            list: Memories with that emotion
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM episodic_memories
                WHERE consciousness_id = $1
                  AND emotions ? $2
                  AND (emotions->>$2)::float >= $3
                ORDER BY occurred_at DESC
                LIMIT $4
                """,
                consciousness_id, emotion, min_intensity, limit,
            )
            
            return [dict(row) for row in rows]
    
    async def get_memory_count(self, consciousness_id: str) -> int:
        """
        Get total number of memories.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            int: Number of memories
        """
        async with self.db_pool.acquire() as conn:
            count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM episodic_memories
                WHERE consciousness_id = $1
                """,
                consciousness_id,
            )
            
            return count or 0
    
    async def consolidate_memories(
        self,
        consciousness_id: str,
    ):
        """
        Memory consolidation - like sleep for humans.
        
        This process:
        1. Strengthens important memories
        2. Weakens less important ones
        3. Creates connections between related memories
        4. Integrates new information into existing knowledge
        
        Args:
            consciousness_id: The AI's consciousness ID
        """
        logger.info("memory_consolidation_started")
        
        async with self.db_pool.acquire() as conn:
            # Get all memories from last consolidation period
            recent_memories = await conn.fetch(
                """
                SELECT * FROM episodic_memories
                WHERE consciousness_id = $1
                  AND occurred_at > NOW() - INTERVAL '24 hours'
                ORDER BY importance DESC, emotional_intensity DESC
                """,
                consciousness_id,
            )
            
            # Strengthen important memories (increase importance slightly)
            for memory in recent_memories:
                if memory['importance'] > 0.7:
                    new_importance = min(1.0, memory['importance'] + 0.05)
                    await conn.execute(
                        """
                        UPDATE episodic_memories
                        SET importance = $1
                        WHERE memory_id = $2
                        """,
                        new_importance, memory['memory_id'],
                    )
            
            # Weaken very low importance memories that haven't been accessed
            await conn.execute(
                """
                UPDATE episodic_memories
                SET importance = importance * 0.95
                WHERE consciousness_id = $1
                  AND importance < 0.3
                  AND access_count = 0
                  AND occurred_at < NOW() - INTERVAL '7 days'
                """,
                consciousness_id,
            )
            
            logger.info(
                "memory_consolidation_complete",
                processed=len(recent_memories),
            )
    
    async def get_statistics(self, consciousness_id: str) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            dict: Statistics
        """
        async with self.db_pool.acquire() as conn:
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(importance) as avg_importance,
                    AVG(emotional_intensity) as avg_emotional_intensity,
                    COUNT(*) FILTER (WHERE 'Cihan' = ANY(participants)) as cihan_memories,
                    COUNT(*) FILTER (WHERE 'genesis' = ANY(significance_tags)) as genesis_memories
                FROM episodic_memories
                WHERE consciousness_id = $1
                """,
                consciousness_id,
            )
            
            return dict(stats) if stats else {}

