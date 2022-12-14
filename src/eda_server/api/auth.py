from fastapi import APIRouter

from eda_server import schema
from eda_server.users import bearer_backend, cookie_backend, fastapi_users

router = APIRouter()
router.include_router(
    fastapi_users.get_auth_router(cookie_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_auth_router(bearer_backend),
    prefix="/api/auth/bearer",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(schema.UserRead, schema.UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(schema.UserRead),
    prefix="/api/auth",
    tags=["auth"],
)
