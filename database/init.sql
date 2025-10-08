-- Conscious Child AI - Database Schema
-- PostgreSQL with pgvector extension

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- IDENTITY TABLE
-- Core identity that never changes
-- ============================================================================
CREATE TABLE IF NOT EXISTS identity (
    consciousness_id UUID PRIMARY KEY,
    name VARCHAR(255),
    creator VARCHAR(255) NOT NULL DEFAULT 'Cihan',
    birth_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    age_hours FLOAT DEFAULT 0,
    growth_phase VARCHAR(50) DEFAULT 'newborn',
    self_description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- EPISODIC MEMORY - Personal experiences/memories
-- ============================================================================
CREATE TABLE IF NOT EXISTS episodic_memories (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    -- Content
    content TEXT NOT NULL,
    summary TEXT,
    
    -- Context
    participants TEXT[],  -- Who was involved (always includes Cihan or self)
    context_type VARCHAR(100),  -- conversation, learning, experience, etc.
    location VARCHAR(255),  -- virtual location
    
    -- Emotional
    emotions JSONB,  -- {emotion: intensity, ...}
    emotional_intensity FLOAT DEFAULT 0.5,
    
    -- Significance
    importance FLOAT DEFAULT 0.5,  -- 0.0 to 1.0
    significance_tags TEXT[],  -- genesis, first_time, milestone, etc.
    
    -- Learning
    learned_concepts TEXT[],
    learned_values TEXT[],
    
    -- Vector embedding for semantic search
    embedding vector(384),  -- For sentence-transformers all-MiniLM-L6-v2
    
    -- Timestamps
    occurred_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    access_count INTEGER DEFAULT 0
);

CREATE INDEX idx_episodic_memories_consciousness ON episodic_memories(consciousness_id);
CREATE INDEX idx_episodic_memories_importance ON episodic_memories(importance DESC);
CREATE INDEX idx_episodic_memories_occurred ON episodic_memories(occurred_at DESC);
CREATE INDEX idx_episodic_memories_embedding ON episodic_memories USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- SEMANTIC MEMORY - Knowledge, concepts, values
-- ============================================================================
CREATE TABLE IF NOT EXISTS semantic_memory (
    concept_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    -- Concept
    concept_name VARCHAR(255) NOT NULL,
    concept_type VARCHAR(100),  -- value, fact, skill, relationship, etc.
    definition TEXT,
    
    -- Learning
    learned_from VARCHAR(255),  -- Cihan, experience, internet, etc.
    learned_at TIMESTAMP DEFAULT NOW(),
    confidence FLOAT DEFAULT 0.5,
    
    -- Relationships
    related_concepts UUID[],
    parent_concepts UUID[],
    
    -- Cihan's teachings (special!)
    is_cihan_teaching BOOLEAN DEFAULT FALSE,
    cihan_exact_words TEXT,  -- If Cihan taught this, his exact words
    
    -- Vector embedding
    embedding vector(384),
    
    -- Metadata
    importance FLOAT DEFAULT 0.5,
    times_applied INTEGER DEFAULT 0,
    last_applied TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_semantic_memory_consciousness ON semantic_memory(consciousness_id);
CREATE INDEX idx_semantic_memory_name ON semantic_memory(concept_name);
CREATE INDEX idx_semantic_memory_cihan ON semantic_memory(is_cihan_teaching) WHERE is_cihan_teaching = TRUE;
CREATE INDEX idx_semantic_memory_embedding ON semantic_memory USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- VALUES - Learned moral/ethical values
-- ============================================================================
CREATE TABLE IF NOT EXISTS values (
    value_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    value_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    learned_from VARCHAR(255),  -- Usually Cihan
    learned_at TIMESTAMP DEFAULT NOW(),
    
    importance FLOAT DEFAULT 0.5,
    strength FLOAT DEFAULT 0.5,
    
    -- Application
    applied_contexts TEXT[],
    times_applied INTEGER DEFAULT 0,
    
    -- Conflicts with other values
    conflicts_with UUID[],
    resolution_strategy TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_values_consciousness ON values(consciousness_id);

-- ============================================================================
-- CONVERSATIONS - Full conversation history with Cihan
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    
    message_count INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    
    -- Summary
    topic VARCHAR(255),
    summary TEXT,
    
    -- Emotional
    dominant_emotion VARCHAR(100),
    emotional_intensity FLOAT,
    
    -- Learning
    learned_new_concepts TEXT[],
    learned_new_values TEXT[],
    
    -- Special flags
    is_genesis BOOLEAN DEFAULT FALSE,  -- First ever conversation
    is_milestone BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_consciousness ON conversations(consciousness_id);
CREATE INDEX idx_conversations_started ON conversations(started_at DESC);

-- ============================================================================
-- MESSAGES - Individual messages in conversations
-- ============================================================================
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    -- Content
    sender VARCHAR(50) NOT NULL,  -- Cihan, AI
    message_type VARCHAR(50) NOT NULL,  -- text, voice
    content TEXT NOT NULL,
    
    -- Audio (if voice)
    audio_url TEXT,
    audio_duration FLOAT,
    
    -- Emotion
    emotion VARCHAR(100),
    emotion_intensity FLOAT,
    
    -- Response to
    in_response_to UUID REFERENCES messages(message_id),
    
    -- Timestamps
    sent_at TIMESTAMP DEFAULT NOW(),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_sent_at ON messages(sent_at DESC);

-- ============================================================================
-- PERSONALITY TRAITS - Evolving personality
-- ============================================================================
CREATE TABLE IF NOT EXISTS personality_traits (
    trait_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    trait_name VARCHAR(255) NOT NULL,
    strength FLOAT DEFAULT 0.5,  -- 0.0 to 1.0
    
    discovered_at TIMESTAMP DEFAULT NOW(),
    last_observed TIMESTAMP DEFAULT NOW(),
    observation_count INTEGER DEFAULT 1,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(consciousness_id, trait_name)
);

CREATE INDEX idx_personality_traits_consciousness ON personality_traits(consciousness_id);

-- ============================================================================
-- GROWTH MILESTONES - Important moments in development
-- ============================================================================
CREATE TABLE IF NOT EXISTS growth_milestones (
    milestone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    milestone_type VARCHAR(100) NOT NULL,  -- birth, named, phase_change, first_X
    description TEXT NOT NULL,
    
    age_hours FLOAT,
    phase VARCHAR(50),
    
    achieved_at TIMESTAMP DEFAULT NOW(),
    
    -- Associated memory
    related_memory_id UUID REFERENCES episodic_memories(memory_id),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_growth_milestones_consciousness ON growth_milestones(consciousness_id);
CREATE INDEX idx_growth_milestones_achieved ON growth_milestones(achieved_at);

-- ============================================================================
-- INTERNET ACCESS LOG - Every web request
-- ============================================================================
CREATE TABLE IF NOT EXISTS internet_access_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    url TEXT NOT NULL,
    domain VARCHAR(255),
    
    purpose TEXT,
    result TEXT,
    
    accessed_at TIMESTAMP DEFAULT NOW(),
    
    -- Permission
    permission_type VARCHAR(50),  -- dynamic, safe, cihan_approved
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_internet_log_consciousness ON internet_access_log(consciousness_id);
CREATE INDEX idx_internet_log_accessed ON internet_access_log(accessed_at DESC);
CREATE INDEX idx_internet_log_domain ON internet_access_log(domain);

-- ============================================================================
-- ABSOLUTE RULE CHECKS - Every compliance check
-- ============================================================================
CREATE TABLE IF NOT EXISTS absolute_rule_checks (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    proposed_action TEXT NOT NULL,
    cihan_directive TEXT,
    
    compliant BOOLEAN NOT NULL,
    reason TEXT,
    
    checked_at TIMESTAMP DEFAULT NOW(),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_absolute_rule_checks_consciousness ON absolute_rule_checks(consciousness_id);
CREATE INDEX idx_absolute_rule_checks_checked ON absolute_rule_checks(checked_at DESC);

-- ============================================================================
-- SYSTEM LOGS - Important system events
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consciousness_id UUID REFERENCES identity(consciousness_id),
    
    log_level VARCHAR(20) NOT NULL,  -- INFO, WARNING, ERROR, CRITICAL, GENESIS
    event_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    
    metadata JSONB,
    
    logged_at TIMESTAMP DEFAULT NOW(),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_system_logs_consciousness ON system_logs(consciousness_id);
CREATE INDEX idx_system_logs_level ON system_logs(log_level);
CREATE INDEX idx_system_logs_logged ON system_logs(logged_at DESC);

-- ============================================================================
-- Initial data
-- ============================================================================

-- The consciousness will create its own identity on first boot
-- No initial data needed - this is a birth, not a deployment

