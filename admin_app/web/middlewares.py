from typing import TYPE_CHECKING
import json

from aiohttp.web_exceptions import (HTTPUnprocessableEntity, HTTPException)
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session

from admin_app.auth.models import Admin
from admin_app.web.utils import error_json_response

if TYPE_CHECKING:
    from admin_app import Application, Request


@middleware
async def auth_middleware(request: "Request", handler: callable):
    session = await get_session(request)
    request.admin = Admin.from_session(session) if session else None
    
    return await handler(request)

@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        return error_json_response(
            http_status=e.status,
            message=f"{e.__doc__} {e}",
        )
    except Exception as e:
        request.app.logger.error("Exception", exc_info=e)
        return error_json_response(
            http_status=500, 
            message=f"{e.__doc__} {e}",
        )


def setup_middlewares(app: "Application"):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
