from app.exceptions.scheme import AppException
from app.models import dto
from app.service import user_service
from app.core.security import session
from app.core import dependencies
from fastapi import APIRouter, status, Response, BackgroundTasks, HTTPException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=dto.UserDTO)
async def register(user: dto.UserCreateDTO):
    try:
            return user_service.create_user(user)
    except AppException as e:
        raise e
    except ValueError as e:
        logger.warning(f"Validation error in register: {str(e)}")
        raise AppException(message=f"Validation error: {str(e)}", status_code=422)
    except Exception as e:
        logger.error(f"Unexpected error in register: {str(e)}")
        raise AppException(message="Registration failed. Please try again.", status_code=500)

@router.post("/login", status_code=status.HTTP_200_OK, response_model=str)
async def login(obj: dto.UserLoginDTO, res: Response):
    """Login user with rate limiting and validation"""
    try:
        return await session.login(obj, res)
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        raise AppException(message="Login failed. Please try again.", status_code=500)


@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(res: Response):
    await session.logout(res)

@router.get("/validate", response_model=dto.Token)
async def check_session(token: dependencies.token_dependency):
    return token
