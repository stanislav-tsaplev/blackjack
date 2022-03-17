import json

from aiohttp_apispec import docs
from aiohttp.web_exceptions import HTTPForbidden

from admin_app.base_classes import View
from admin_app.web.mixins import AuthRequiredMixin
from admin_app.web.utils import json_response
from admin_app.games.schemes import GameSummarySchema#, GameChatsSchema


class GameSummaryView(AuthRequiredMixin, View):
    @docs(
        tags=["admin", "game"],
        summary="Get games info",
        description="Get information about games played",
        responses={
            200: {"description": "Game summary", "schema": GameSummarySchema},
            401: {"description": "Unauthorized"},
            403: {"description": "Invalid credentials"},
        },
    )
    async def get(self):
        query_params = self.request.query
        offset = query_params.get("offset")
        if offset is not None:
            offset = int(offset)
        limit = query_params.get("limit")
        if limit is not None:
            limit = int(limit)

        games_summary = await self.store.games.get_summary(offset, limit)
        return json_response(data=GameSummarySchema().dump(games_summary))
