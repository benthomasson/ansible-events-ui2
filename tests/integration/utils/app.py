from fastapi import FastAPI

from eda_server.app import setup_cors, setup_routes
from eda_server.db.dependency import get_db_session_factory
from eda_server.users import current_active_user
from tests.integration.utils.db import get_admin_user


async def create_test_app(settings, session):
    user = await get_admin_user(session)

    app = FastAPI(title="Ansible Events API")
    app.state.settings = settings

    setup_cors(app)
    setup_routes(app)

    app.dependency_overrides[current_active_user] = lambda: user
    app.dependency_overrides[get_db_session_factory] = lambda: lambda: session

    return app
