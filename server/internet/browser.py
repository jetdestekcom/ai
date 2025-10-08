"""
Web Browser - Internet Access for AI

Allows AI to browse the internet, learn from web content.
Uses httpx for web requests (simple and reliable).
"""

import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)


class WebBrowser:
    """
    Web browser for AI to access internet.
    
    Supports:
    - HTTP requests via httpx
    - Content extraction with BeautifulSoup
    - Safety checking
    """
    
    def __init__(self):
        """Initialize web browser."""
        self.httpx_client = None
        self.is_initialized = False
        
        logger.info("web_browser_created")
    
    async def initialize(self):
        """Initialize HTTP client."""
        logger.info("initializing_web_browser")
        
        # Initialize httpx client
        self.httpx_client = httpx.AsyncClient(
            timeout=settings.WEB_REQUEST_TIMEOUT,
            follow_redirects=True,
            headers={
                'User-Agent': 'ConsciousChildAI/1.0'
            }
        )
        
        self.is_initialized = True
        logger.info("web_browser_initialized")
    
    async def fetch(
        self,
        url: str,
    ) -> Dict[str, Any]:
        """
        Fetch a web page.
        
        Args:
            url: URL to fetch
            
        Returns:
            dict: Page content and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("fetching_url", url=url)
        
        # Safety check (basic)
        if not self._is_safe_url(url):
            logger.warning("unsafe_url_blocked", url=url)
            return {"error": "URL blocked for safety"}
        
        try:
            return await self._fetch_with_httpx(url)
        
        except Exception as e:
            logger.error("fetch_failed", url=url, error=str(e))
            return {"error": str(e)}
    
    async def _fetch_with_httpx(self, url: str) -> Dict[str, Any]:
        """Fetch with httpx."""
        response = await self.httpx_client.get(url)
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        return {
            "url": url,
            "title": title,
            "text": text[:10000],  # Limit to 10000 chars
            "status": response.status_code,
        }
    
    def _is_safe_url(self, url: str) -> bool:
        """Basic safety check for URLs."""
        parsed = urlparse(url)
        
        # Block certain domains (basic blocklist)
        blocked_domains = [
            "malware.com",  # Example
        ]
        
        if any(blocked in parsed.netloc for blocked in blocked_domains):
            return False
        
        return True
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the web.
        
        Args:
            query: Search query
            
        Returns:
            list: Search results
        """
        # Use DuckDuckGo (privacy-friendly)
        from duckduckgo_search import AsyncDDGS
        
        logger.info("searching_web", query=query)
        
        async with AsyncDDGS() as ddgs:
            results = []
            async for result in ddgs.text(query, max_results=10):
                results.append({
                    "title": result.get("title"),
                    "url": result.get("href"),
                    "snippet": result.get("body"),
                })
            
            return results
    
    async def close(self):
        """Close HTTP client."""
        if self.httpx_client:
            await self.httpx_client.aclose()
        
        logger.info("web_browser_closed")

