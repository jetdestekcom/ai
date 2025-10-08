"""
Configuration management using Pydantic Settings.
Loads from environment variables and .env file.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Core settings
    ENVIRONMENT: str = Field(default="production")
    AI_NAME: Optional[str] = Field(default=None)
    BIRTH_TIMESTAMP: Optional[str] = Field(default=None)
    CONSCIOUSNESS_ID: Optional[str] = Field(default=None)
    
    # Server settings
    SERVER_HOST: str = Field(default="0.0.0.0")
    SERVER_PORT: int = Field(default=8000)
    DOMAIN: Optional[str] = Field(default=None)
    
    # Database settings
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB: str = Field(default="conscious_child")
    POSTGRES_USER: str = Field(default="ai_user")
    POSTGRES_PASSWORD: str = Field(default="")
    
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    CHROMA_HOST: str = Field(default="localhost")
    CHROMA_PORT: int = Field(default=8001)
    
    # AI Model settings
    LLM_TYPE: str = Field(default="local")  # local, api, hybrid
    LLM_MODEL_PATH: str = Field(default="./models/llm/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    LLM_API_KEY: Optional[str] = Field(default=None)
    LLM_API_PROVIDER: Optional[str] = Field(default=None)  # claude, openai
    
    WHISPER_MODEL_SIZE: str = Field(default="small")
    WHISPER_DEVICE: str = Field(default="cpu")
    
    TTS_ENGINE: str = Field(default="coqui")
    TTS_MODEL_PATH: str = Field(default="./models/tts/")
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None)
    
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    
    # Security settings
    JWT_SECRET: str = Field(default="CHANGE_THIS_IN_PRODUCTION")
    JWT_EXPIRATION_DAYS: int = Field(default=7)
    ENCRYPTION_KEY: str = Field(default="CHANGE_THIS_IN_PRODUCTION")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])
    
    # Cihan (Creator) settings
    CREATOR_NAME: str = Field(default="Cihan")
    CREATOR_DEVICE_ID: Optional[str] = Field(default=None)
    EMERGENCY_CODE: str = Field(default="CHANGE_THIS")
    
    # Learning settings
    BASE_LEARNING_RATE: float = Field(default=0.001)
    CONSOLIDATION_INTERVAL: int = Field(default=24)  # hours
    EWC_LAMBDA: float = Field(default=0.4)
    
    # Internet settings
    INTERNET_ENABLED: bool = Field(default=True)
    WEB_REQUEST_TIMEOUT: int = Field(default=30)
    WEB_RATE_LIMIT: int = Field(default=100)
    SAFE_BROWSING_API_KEY: Optional[str] = Field(default=None)
    
    # Backup settings
    BACKUP_DIR: str = Field(default="./backups")
    BACKUP_RETENTION_DAYS: int = Field(default=36500)  # 100 years
    
    CLOUD_BACKUP_ENABLED: bool = Field(default=False)
    CLOUD_BACKUP_PROVIDER: Optional[str] = Field(default=None)
    CLOUD_BACKUP_BUCKET: Optional[str] = Field(default=None)
    
    # Monitoring settings
    LOG_LEVEL: str = Field(default="INFO")
    STRUCTURED_LOGGING: bool = Field(default=True)
    METRICS_ENABLED: bool = Field(default=False)
    METRICS_PORT: int = Field(default=9090)
    
    ALERT_EMAIL: Optional[str] = Field(default=None)
    
    # Development settings
    DEBUG: bool = Field(default=False)
    RELOAD: bool = Field(default=False)
    DISABLE_AUTH: bool = Field(default=False)
    
    # Advanced settings
    ATTENTION_THRESHOLD: float = Field(default=0.7)
    EMOTION_SCALE: float = Field(default=1.0)
    CONFIDENCE_THRESHOLD: float = Field(default=0.8)
    WORKING_MEMORY_SIZE: int = Field(default=7)
    PREDICTION_ERROR_WEIGHT: float = Field(default=0.5)
    
    # Absolute Rule protection
    ABSOLUTE_RULE_LOCKED: bool = Field(default=True)
    ABSOLUTE_RULE_HASH: Optional[str] = Field(default=None)
    
    @property
    def DATABASE_URL(self) -> str:
        """PostgreSQL connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Async PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDIS_URL(self) -> str:
        """Redis connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def CHROMA_URL(self) -> str:
        """ChromaDB connection URL."""
        return f"http://{self.CHROMA_HOST}:{self.CHROMA_PORT}"


# Create global settings instance
settings = Settings()

