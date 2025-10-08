"""
Authentication System - Cihan-Only Access

JWT-based authentication with biometric verification support.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm="HS256"
    )
    
    logger.info("access_token_created", expires_at=expire.isoformat())
    
    return encoded_jwt


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Verify JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        dict: Decoded token data
        
    Raises:
        HTTPException: If token invalid
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        
        # Check if token for Cihan
        username = payload.get("sub")
        if username != settings.CREATOR_NAME:
            logger.warning("invalid_user_in_token", user=username)
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return payload
    
    except JWTError as e:
        logger.warning("jwt_verification_failed", error=str(e))
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )


async def get_current_user(token_data: dict = Depends(verify_token)) -> str:
    """
    Get current authenticated user (should always be Cihan).
    
    Args:
        token_data: Decoded token data
        
    Returns:
        str: Username (Cihan)
    """
    username = token_data.get("sub")
    return username


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

