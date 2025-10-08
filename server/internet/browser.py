"""
Web Browser - Internet Access for AI

Allows AI to browse the internet, learn from web content.
Uses Playwright for JavaScript-heavy sites, requests for simple pages.
"""

import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page
import httpx
from bs4 import BeautifulSoup
import structlog

from utils.config import settings

logger = structlog.get_logger(__name__)


class WebBrowser:
    """
    Web browser for AI to access internet.
    
    Supports:
    - Simple HTTP requests
    - JavaScript-heavy sites (Playwright)
    - Content extraction
    - Safety checking
    """
    
    def __init__(self):
        """Initialize web browser."""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.httpx_client = None
        self.is_initialized = False
        
        logger.info("web_browser_created")
    
    async def initialize(self):
        """Initialize browser and HTTP client."""
        logger.info("initializing_web_browser")
        
        # Initialize Playwright (for JS-heavy sites)
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox'],
        )
        
        # Initialize httpx (for simple requests)
        self.httpx_client = httpx.AsyncClient(
            timeout=settings.WEB_REQUEST_TIMEOUT,
            follow_redirects=True,
        )
        
        self.is_initialized = True
        logger.info("web_browser_initialized")
    
    async def fetch(
        self,
        url: str,
        use_browser: bool = False,
    ) -> Dict[str, Any]:
        """
        Fetch a web page.
        
        Args:
            url: URL to fetch
            use_browser: Use Playwright (for JS) or httpx (faster)
            
        Returns:
            dict: Page content and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("fetching_url", url=url, use_browser=use_browser)
        
        # Safety check (basic)
        if not self._is_safe_url(url):
            logger.warning("unsafe_url_blocked", url=url)
            return {"error": "URL blocked for safety"}
        
        try:
            if use_browser:
                return await self._fetch_with_playwright(url)
            else:
                return await self._fetch_with_httpx(url)
        
        except Exception as e:
            logger.error("fetch_failed", url=url, error=str(e))
            return {"error": str(e)}
    
    async def _fetch_with_httpx(self, url: str) -> Dict[str, Any]:
        """Fetch with httpx (fast, no JS)."""
        response = await self.httpx_client.get(url)
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        return {
            "url": url,
            "title": title,
            "text": text[:5000],  # Limit to 5000 chars
            "status": response.status_code,
        }
    
    async def _fetch_with_playwright(self, url: str) -> Dict[str, Any]:
        """Fetch with Playwright (handles JS)."""
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle')
            
            # Get title
            title = await page.title()
            
            # Get text content
            text = await page.inner_text('body')
            
            return {
                "url": url,
                "title": title,
                "text": text[:5000],
                "status": 200,
            }
        
        finally:
            await page.close()
    
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
        """Close browser and clients."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        if self.httpx_client:
            await self.httpx_client.aclose()
        
        logger.info("web_browser_closed")

