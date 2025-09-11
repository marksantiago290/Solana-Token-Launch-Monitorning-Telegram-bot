import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class APIClient:
    """Client for making API requests to the token analyzer API server"""
    
    def __init__(self, timeout=600):  # Default timeout of 60 seconds
        self._session = None
        self.timeout = timeout
    
    async def _get_session(self):
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def get(self, url, params=None, timeout=None):
        """Make a GET request to the API server"""
        # Use the provided timeout or fall back to the default
        request_timeout = timeout or self.timeout
        
        # Create a session with the specified timeout
        session = await self._get_session()
        
        try:
            # Set a timeout for this specific request
            timeout_ctx = aiohttp.ClientTimeout(total=request_timeout)
            
            async with session.get(url, params=params, timeout=timeout_ctx) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"API error: {response.status} - {error_text}")
                    return {"error": f"API error: {response.status}", "detail": error_text}
        except asyncio.TimeoutError:
            logger.error(f"Request timed out after {request_timeout} seconds for URL: {url}")
            return {"error": f"Request timed out after {request_timeout} seconds", "detail": "The API server took too long to respond"}
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection error for URL {url}: {str(e)}")
            return {"error": f"Connection error", "detail": str(e)}
        except Exception as e:
            logger.error(f"Request error for URL {url}: {str(e)}")
            return {"error": f"Request failed: {str(e)}", "detail": str(e)}

# Create a singleton instance
api_client = APIClient()
