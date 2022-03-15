import json

from aiohttp_apispec import docs, request_schema
from aiohttp_session import new_session
from aiohttp.web_exceptions import HTTPForbidden

from admin_app.base_classes import View
from admin_app.web.mixins import AuthRequiredMixin
from admin_app.web.utils import json_response
from admin_app.game_info.schemes.summary import GameInfoSummarySchema


class GameInfoSummaryView(AuthRequiredMixin, View):
    @docs(
        tags=["admin", "game"],
        summary="Get games info",
        description="Get information about games played",
        responses={
            200: {"description": "Current admin", "schema": GameInfoSummarySchema},
            401: {"description": "Unauthorized"},
            403: {"description": "Invalid credentials"},
        },
    )
    async def get(self):
        return json_response(data=GameInfoSummarySchema().dump(...))