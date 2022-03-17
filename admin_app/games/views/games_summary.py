import json

from aiohttp_apispec import docs, querystring_schema
from aiohttp.web_exceptions import HTTPForbidden

from admin_app.base_classes import View
from admin_app.web.mixins import AuthRequiredMixin
from admin_app.web.utils import json_response
from admin_app.games.schemes import GameSummarySchema, PaginationQuerystringSchema


# class GameSummaryView(AuthRequiredMixin, View):
class GameSummaryView(View):
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
    @querystring_schema(PaginationQuerystringSchema)
    async def get(self):
        query_params = self.request.query
        offset = query_params.get("offset")
        limit = query_params.get("limit")

        games_summary = await self.store.games.get_summary(offset, limit)
        return json_response(data=GameSummarySchema().dump(games_summary))
