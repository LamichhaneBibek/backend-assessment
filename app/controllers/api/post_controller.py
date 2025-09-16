from fastapi import APIRouter
from fastapi import Query, HTTPException, status
from typing import Optional
from uuid import UUID
from app.models import dto
from app.core import dependencies
from app.service import user_service
from app.service.post_service import PostsService

router = APIRouter(
    prefix="/posts",
    tags=["Post"]
)


@router.get("", response_model=dto.PostListResponse)
async def get_all_posts(page: int = Query(1, ge=1, description="Page number"),
per_page: int = Query(10, ge=1, le=100, description="Posts per page"),
search: Optional[str] = Query(None, description="Search in title and body")):
    posts_service = PostsService()

    try:
        return await posts_service.get_posts(
            page=page,
            per_page=per_page,
            search=search
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch posts: {str(e)}"
        )


@router.get("/{id}", response_model=dto.Post)
async def get_post_by_id(id: int):
    posts_service = PostsService()

    try:
        post = await posts_service.get_post_by_id(id)

        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch post: {str(e)}"
        )
