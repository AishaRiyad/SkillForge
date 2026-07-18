from fastapi import APIRouter

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.categories import router as categories_router
from app.api.v1.routes.courses import router as courses_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.users import router as users_router

router = APIRouter()

router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(categories_router)
router.include_router(courses_router)
