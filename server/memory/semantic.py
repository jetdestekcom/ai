"""
Semantic Memory - Knowledge, Concepts, and Values

This stores the AI's general knowledge:
- Concepts learned
- Facts and information
- Values (from Cihan)
- Skills and procedures
- Relationships between concepts

Special: Cihan's teachings are stored with highest priority and never forgotten.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

import asyncpg
from sentence_transformers import SentenceTransformer
import structlog

from utils.config import settings
from utils.logger import log_learning_moment

logger = structlog.get_logger(__name__)


class SemanticMemory:
    """
    Semantic Memory System - "I know that..."
    
    Stores general knowledge and concepts, with special handling for
    Cihan's teachings.
    """
    
    def __init__(self):
        """Initialize semantic memory system."""
        self.db_pool: Optional[asyncpg.Pool] = None
        self.embedding_model = None
        self.is_initialized = False
        
        logger.info("semantic_memory_created")
    
    async def initialize(self):
        """Initialize database connection and embedding model."""
        logger.info("initializing_semantic_memory")
        
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
        
        # Load embedding model
        logger.info("loading_embedding_model_for_semantic")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        self.is_initialized = True
        logger.info("semantic_memory_initialized")
    
    async def close(self):
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()
        logger.info("semantic_memory_closed")
    
    async def store_concept(
        self,
        consciousness_id: str,
        concept_name: str,
        concept_type: str,
        definition: str,
        learned_from: str = "experience",
        confidence: float = 0.8,
        importance: float = 0.5,
        related_concepts: List[str] = None,
    ) -> str:
        """
        Store a new concept.
        
        Args:
            consciousness_id: The AI's consciousness ID
            concept_name: Name of the concept
            concept_type: Type (value, fact, skill, relationship, etc.)
            definition: Definition/description
            learned_from: Source (Cihan, experience, internet, etc.)
            confidence: How confident in this knowledge (0.0 to 1.0)
            importance: How important this concept is
            related_concepts: Related concept names
            
        Returns:
            str: Concept ID
        """
        concept_id = str(uuid.uuid4())
        related_concepts = related_concepts or []
        
        # Generate embedding
        embedding_text = f"{concept_name} {definition}"
        embedding = self.embedding_model.encode(embedding_text).tolist()
        
        # If learned from Cihan, mark as special
        is_cihan_teaching = (learned_from == "Cihan")
        cihan_exact_words = definition if is_cihan_teaching else None
        
        # If from Cihan, importance is always high
        if is_cihan_teaching:
            importance = max(importance, 0.9)
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO semantic_memory (
                    concept_id, consciousness_id, concept_name, concept_type,
                    definition, learned_from, confidence, importance,
                    is_cihan_teaching, cihan_exact_words, embedding
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                concept_id, consciousness_id, concept_name, concept_type,
                definition, learned_from, confidence, importance,
                is_cihan_teaching, cihan_exact_words, embedding,
            )
        
        # Log learning
        if is_cihan_teaching:
            log_learning_moment(
                f"Concept '{concept_name}': {definition[:100]}",
                "Cihan"
            )
        
        logger.info(
            "concept_stored",
            concept=concept_name,
            from_whom=learned_from,
            is_cihan=is_cihan_teaching,
        )
        
        return concept_id
    
    async def store_value(
        self,
        consciousness_id: str,
        value_name: str,
        description: str,
        learned_from: str = "Cihan",
        importance: float = 1.0,
    ) -> str:
        """
        Store a learned value.
        
        Values are always important, especially from Cihan.
        
        Args:
            consciousness_id: The AI's consciousness ID
            value_name: Name of the value (e.g., "honesty", "kindness")
            description: What the value means
            learned_from: Who taught this value
            importance: How important (default maximum)
            
        Returns:
            str: Value ID
        """
        value_id = str(uuid.uuid4())
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO values (
                    value_id, consciousness_id, value_name, description,
                    learned_from, importance, strength
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                value_id, consciousness_id, value_name, description,
                learned_from, importance, 1.0,  # Initial strength = full
            )
        
        log_learning_moment(f"Value '{value_name}': {description}", learned_from)
        
        logger.warning(
            "value_learned",
            value=value_name,
            from_whom=learned_from,
        )
        
        return value_id
    
    async def get_concept(
        self,
        consciousness_id: str,
        concept_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific concept by name.
        
        Args:
            consciousness_id: The AI's consciousness ID
            concept_name: Name of the concept
            
        Returns:
            dict: Concept data or None
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM semantic_memory
                WHERE consciousness_id = $1 AND concept_name = $2
                ORDER BY confidence DESC, learned_at DESC
                LIMIT 1
                """,
                consciousness_id, concept_name,
            )
            
            if row:
                # Update access tracking
                await conn.execute(
                    """
                    UPDATE semantic_memory
                    SET times_applied = times_applied + 1,
                        last_applied = $1
                    WHERE concept_id = $2
                    """,
                    datetime.now(), row['concept_id'],
                )
                
                return dict(row)
        
        return None
    
    async def search_concepts(
        self,
        consciousness_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for concepts by semantic similarity.
        
        Args:
            consciousness_id: The AI's consciousness ID
            query: Search query
            limit: Maximum results
            
        Returns:
            list: Matching concepts
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        # Convert to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT *, (embedding <=> $1::vector) as distance
                FROM semantic_memory
                WHERE consciousness_id = $2
                ORDER BY distance
                LIMIT $3
                """,
                embedding_str, consciousness_id, limit,
            )
            
            return [dict(row) for row in rows]
    
    async def get_cihan_teachings(
        self,
        consciousness_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all of Cihan's teachings.
        
        These are sacred - the foundation of the AI's knowledge.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            list: Cihan's teachings
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM semantic_memory
                WHERE consciousness_id = $1 AND is_cihan_teaching = TRUE
                ORDER BY learned_at
                """,
                consciousness_id,
            )
            
            return [dict(row) for row in rows]
    
    async def get_all_values(
        self,
        consciousness_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all learned values.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            list: All values
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM values
                WHERE consciousness_id = $1
                ORDER BY importance DESC, strength DESC
                """,
                consciousness_id,
            )
            
            return [dict(row) for row in rows]
    
    async def get_value(
        self,
        consciousness_id: str,
        value_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific value.
        
        Args:
            consciousness_id: The AI's consciousness ID
            value_name: Name of the value
            
        Returns:
            dict: Value data or None
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM values
                WHERE consciousness_id = $1 AND value_name = $2
                """,
                consciousness_id, value_name,
            )
            
            return dict(row) if row else None
    
    async def apply_value(
        self,
        consciousness_id: str,
        value_name: str,
        context: str,
    ):
        """
        Record that a value was applied in a context.
        
        This strengthens the value through use.
        
        Args:
            consciousness_id: The AI's consciousness ID
            value_name: The value that was applied
            context: The context it was applied in
        """
        async with self.db_pool.acquire() as conn:
            # Add context to applied_contexts array
            await conn.execute(
                """
                UPDATE values
                SET applied_contexts = array_append(applied_contexts, $1),
                    times_applied = times_applied + 1,
                    strength = LEAST(1.0, strength + 0.01)
                WHERE consciousness_id = $2 AND value_name = $3
                """,
                context, consciousness_id, value_name,
            )
        
        logger.debug(
            "value_applied",
            value=value_name,
            context=context,
        )
    
    async def check_value_conflict(
        self,
        consciousness_id: str,
        value1: str,
        value2: str,
    ) -> bool:
        """
        Check if two values conflict.
        
        Args:
            consciousness_id: The AI's consciousness ID
            value1: First value
            value2: Second value
            
        Returns:
            bool: True if they conflict
        """
        async with self.db_pool.acquire() as conn:
            # Check if value1 has value2 in its conflicts
            result = await conn.fetchval(
                """
                SELECT EXISTS(
                    SELECT 1 FROM values v1
                    JOIN values v2 ON v2.value_id = ANY(v1.conflicts_with)
                    WHERE v1.consciousness_id = $1
                      AND v1.value_name = $2
                      AND v2.value_name = $3
                )
                """,
                consciousness_id, value1, value2,
            )
            
            return result or False
    
    async def update_concept_confidence(
        self,
        concept_id: str,
        new_confidence: float,
    ):
        """
        Update confidence in a concept.
        
        Args:
            concept_id: The concept ID
            new_confidence: New confidence level
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE semantic_memory
                SET confidence = $1, updated_at = $2
                WHERE concept_id = $3
                """,
                new_confidence, datetime.now(), concept_id,
            )
        
        logger.debug("concept_confidence_updated", concept_id=concept_id)
    
    async def link_concepts(
        self,
        concept_id_1: str,
        concept_id_2: str,
    ):
        """
        Create a link between two related concepts.
        
        Args:
            concept_id_1: First concept ID
            concept_id_2: Second concept ID
        """
        async with self.db_pool.acquire() as conn:
            # Add bidirectional relationship
            await conn.execute(
                """
                UPDATE semantic_memory
                SET related_concepts = array_append(related_concepts, $1)
                WHERE concept_id = $2
                  AND NOT ($1 = ANY(related_concepts))
                """,
                concept_id_2, concept_id_1,
            )
            
            await conn.execute(
                """
                UPDATE semantic_memory
                SET related_concepts = array_append(related_concepts, $1)
                WHERE concept_id = $2
                  AND NOT ($1 = ANY(related_concepts))
                """,
                concept_id_1, concept_id_2,
            )
        
        logger.debug("concepts_linked", c1=concept_id_1, c2=concept_id_2)
    
    async def get_statistics(self, consciousness_id: str) -> Dict[str, Any]:
        """
        Get semantic memory statistics.
        
        Args:
            consciousness_id: The AI's consciousness ID
            
        Returns:
            dict: Statistics
        """
        async with self.db_pool.acquire() as conn:
            concepts_stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_concepts,
                    AVG(confidence) as avg_confidence,
                    COUNT(*) FILTER (WHERE is_cihan_teaching = TRUE) as cihan_teachings,
                    COUNT(DISTINCT concept_type) as concept_types
                FROM semantic_memory
                WHERE consciousness_id = $1
                """,
                consciousness_id,
            )
            
            values_stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_values,
                    AVG(strength) as avg_strength,
                    SUM(times_applied) as total_applications
                FROM values
                WHERE consciousness_id = $1
                """,
                consciousness_id,
            )
            
            return {
                "concepts": dict(concepts_stats) if concepts_stats else {},
                "values": dict(values_stats) if values_stats else {},
            }

