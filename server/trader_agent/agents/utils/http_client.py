"""
Generic HTTP client with retry, backoff, and optional caching.
Prevents each agent from re-implementing API fetch logic.
"""
import os
import json
import time
import hashlib
import random
import logging
from typing import Dict, Any, Optional, Union
from functools import lru_cache
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Default headers that work well with most APIs
DEFAULT_HEADERS = {
    "accept": "application/json, */*",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
}

# Cache directory for persistent caching
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_key(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """Generate a unique cache key based on URL and headers."""
    cache_data = url
    if headers:
        # Include relevant headers in cache key
        sorted_headers = sorted(headers.items())
        cache_data += str(sorted_headers)
    return hashlib.md5(cache_data.encode("utf-8")).hexdigest()


def _cache_path(cache_key: str) -> str:
    """Get the file path for a cache key."""
    return os.path.join(CACHE_DIR, cache_key + ".json")


def _load_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """Load data from cache file if it exists and is valid."""
    cache_file = _cache_path(cache_key)
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
            
        # Check if cache has expired (optional timestamp-based expiry)
        if "timestamp" in cached_data:
            cache_age = time.time() - cached_data["timestamp"]
            # Cache expires after 1 hour by default
            if cache_age > 3600:
                os.remove(cache_file)
                return None
                
        return cached_data.get("data")
    except (json.JSONDecodeError, OSError, KeyError) as e:
        logger.warning(f"Failed to load cache for key {cache_key}: {e}")
        # Remove corrupted cache file
        try:
            os.remove(cache_file)
        except OSError:
            pass
        return None


def _save_to_cache(cache_key: str, data: Dict[str, Any]) -> None:
    """Save data to cache file with timestamp."""
    cache_file = _cache_path(cache_key)
    try:
        cache_data = {
            "timestamp": time.time(),
            "data": data
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except (OSError, TypeError) as e:
        logger.warning(f"Failed to save cache for key {cache_key}: {e}")


def _create_session_with_retries(retries: int = 3) -> requests.Session:
    """Create a requests session with retry strategy."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def get_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    use_cache: bool = True,
    retries: int = 3,
    backoff_factor: float = 0.8,
    timeout: int = 20,
    cache_ttl: int = 3600
) -> Optional[Dict[str, Any]]:
    """
    Generic HTTP GET request with retry, backoff, and caching.
    
    Args:
        url: The URL to fetch
        headers: Optional headers to include in the request
        use_cache: Whether to use caching (default: True)
        retries: Number of retry attempts (default: 3)
        backoff_factor: Exponential backoff factor (default: 0.8)
        timeout: Request timeout in seconds (default: 20)
        cache_ttl: Cache time-to-live in seconds (default: 3600)
    
    Returns:
        JSON response as dict, or None if request fails
    """
    # Merge default headers with provided headers
    request_headers = DEFAULT_HEADERS.copy()
    if headers:
        request_headers.update(headers)
    
    # Check cache first
    cache_key = _cache_key(url, request_headers) if use_cache else None
    if use_cache and cache_key:
        cached_data = _load_from_cache(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache hit for URL: {url}")
            return cached_data
    
    # Make the request with retries
    last_exception = None
    
    for attempt in range(retries):
        try:
            logger.debug(f"Attempting request to {url} (attempt {attempt + 1}/{retries})")
            
            response = requests.get(
                url,
                headers=request_headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Save to cache if enabled
            if use_cache and cache_key:
                _save_to_cache(cache_key, data)
                logger.debug(f"Cached response for URL: {url}")
            
            logger.debug(f"Successfully fetched data from {url}")
            return data
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
            
            # Don't retry on client errors (4xx)
            if hasattr(e, 'response') and e.response is not None:
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error {e.response.status_code}, not retrying")
                    break
            
            # Calculate backoff time with jitter
            if attempt < retries - 1:  # Don't sleep on last attempt
                sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0.1, 0.3)
                logger.debug(f"Backing off for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        except (json.JSONDecodeError, ValueError) as e:
            last_exception = e
            logger.error(f"Failed to parse JSON response: {e}")
            break  # Don't retry JSON parsing errors
    
    logger.error(f"All retry attempts failed for {url}")
    if last_exception:
        logger.error(f"Last exception: {last_exception}")
    
    return None


def post_json(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    retries: int = 3,
    backoff_factor: float = 0.8,
    timeout: int = 20
) -> Optional[Dict[str, Any]]:
    """
    Generic HTTP POST request with retry and backoff.
    
    Args:
        url: The URL to post to
        data: JSON data to send in request body
        headers: Optional headers to include in the request
        retries: Number of retry attempts (default: 3)
        backoff_factor: Exponential backoff factor (default: 0.8)
        timeout: Request timeout in seconds (default: 20)
    
    Returns:
        JSON response as dict, or None if request fails
    """
    # Merge default headers with provided headers
    request_headers = DEFAULT_HEADERS.copy()
    request_headers["content-type"] = "application/json"
    if headers:
        request_headers.update(headers)
    
    last_exception = None
    
    for attempt in range(retries):
        try:
            logger.debug(f"Attempting POST to {url} (attempt {attempt + 1}/{retries})")
            
            response = requests.post(
                url,
                json=data,
                headers=request_headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            logger.debug(f"Successfully posted data to {url}")
            return result
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            logger.warning(f"POST request failed (attempt {attempt + 1}/{retries}): {e}")
            
            # Don't retry on client errors (4xx)
            if hasattr(e, 'response') and e.response is not None:
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error {e.response.status_code}, not retrying")
                    break
            
            # Calculate backoff time with jitter
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0.1, 0.3)
                logger.debug(f"Backing off for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        except (json.JSONDecodeError, ValueError) as e:
            last_exception = e
            logger.error(f"Failed to parse JSON response: {e}")
            break
    
    logger.error(f"All POST retry attempts failed for {url}")
    if last_exception:
        logger.error(f"Last exception: {last_exception}")
    
    return None


def clear_cache() -> None:
    """Clear all cached files."""
    try:
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith(".json"):
                os.remove(os.path.join(CACHE_DIR, filename))
        logger.info("Cache cleared successfully")
    except OSError as e:
        logger.error(f"Failed to clear cache: {e}")


@lru_cache(maxsize=128)
def get_cached_json(url: str, headers_str: str = "") -> Optional[Dict[str, Any]]:
    """
    In-memory cached version of get_json using functools.lru_cache.
    
    Note: headers must be converted to string for caching compatibility.
    Use this for frequently accessed, rarely changing data.
    """
    headers = json.loads(headers_str) if headers_str else None
    return get_json(url, headers=headers, use_cache=False)  # Disable file cache since we're using memory cache