import json
import math
from typing import List, Optional, Dict, Any
import httpx
import redis
from redis import Redis

from app.core.config import CONFIG
from app.models.dto import Post, PostListResponse


class PostsService:
    def __init__(self):
        self.redis_client: Redis = redis.from_url(CONFIG.REDIS_URL, decode_responses=True)
        self.posts_api_url = CONFIG.POSTS_API_URL
        self.cache_expire = CONFIG.CACHE_EXPIRE_IN_SECONDS
        self.cache_key_prefix = CONFIG.POSTS_CACHE_KEY_PREFIX

    async def _fetch_posts_from_api(self) -> List[Dict[str, Any]]:
        """
        Fetch posts from external API
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.posts_api_url)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Error fetching posts from API: {str(e)}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP error fetching posts: {e.response.status_code}")

    def _get_cached_posts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached posts from Redis
        """
        try:
            cache_key = f"{self.cache_key_prefix}:all"
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                return json.loads(cached_data)

            return None
        except redis.RedisError:
            # If Redis is down, return None to fetch from API
            return None

    def _cache_posts(self, posts: List[Dict[str, Any]]) -> None:
        """
        Cache posts in Redis
        """
        try:
            cache_key = f"{self.cache_key_prefix}:all"
            self.redis_client.setex(
                cache_key,
                self.cache_expire,
                json.dumps(posts)
            )
        except redis.RedisError:
            # If Redis is down, just continue without caching
            pass

    def _filter_posts(
        self,
        posts: List[Dict[str, Any]],
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter posts by search query
        """
        if not search:
            return posts

        search_lower = search.lower()
        filtered_posts = []

        for post in posts:
            title = post.get('title', '').lower()
            body = post.get('body', '').lower()

            if search_lower in title or search_lower in body:
                filtered_posts.append(post)

        return filtered_posts

    def _paginate_posts(
        self,
        posts: List[Dict[str, Any]],
        page: int = 1,
        per_page: int = 10
    ) -> tuple[List[Dict[str, Any]], int, bool, bool]:
        """
        Paginate posts list
        """
        total = len(posts)

        if total == 0:
            return [], 0, False, False

        # Calculate pagination
        total_pages = math.ceil(total / per_page)
        start = (page - 1) * per_page
        end = start + per_page

        paginated_posts = posts[start:end]

        has_next = page < total_pages
        has_prev = page > 1

        return paginated_posts, total, has_next, has_prev

    async def get_posts(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None
    ) -> PostListResponse:
        """
        Get posts with caching, pagination, and search
        """
        # Try to get from cache first
        posts_data = self._get_cached_posts()

        # If not in cache, fetch from API
        if posts_data is None:
            posts_data = await self._fetch_posts_from_api()
            self._cache_posts(posts_data)

        # Apply search filter
        filtered_posts = self._filter_posts(posts_data, search)

        # Apply pagination
        paginated_posts, total, has_next, has_prev = self._paginate_posts(
            filtered_posts, page, per_page
        )

        # Convert to Pydantic models
        posts = [Post(**post) for post in paginated_posts]

        return PostListResponse(
            posts=posts,
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )

    async def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """
        Get a specific post by ID
        """
        # Try to get from cache first
        posts_data = self._get_cached_posts()

        # If not in cache, fetch from API
        if posts_data is None:
            posts_data = await self._fetch_posts_from_api()
            self._cache_posts(posts_data)

        # Find the post by ID
        for post_data in posts_data:
            if post_data.get('id') == post_id:
                return Post(**post_data)

        return None

    def clear_cache(self) -> None:
        """
        Clear posts cache
        """
        try:
            cache_key = f"{self.cache_key_prefix}:all"
            self.redis_client.delete(cache_key)
        except redis.RedisError:
            pass

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache information for debugging
        """
        try:
            cache_key = f"{self.cache_key_prefix}:all"
            exists = self.redis_client.exists(cache_key)
            ttl = self.redis_client.ttl(cache_key)

            return {
                "cache_key": cache_key,
                "exists": bool(exists),
                "ttl": ttl,
                "cache_expire": self.cache_expire
            }
        except redis.RedisError as e:
            return {
                "error": str(e),
                "cache_available": False
            }
