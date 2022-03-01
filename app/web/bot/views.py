import json
from dataclasses import asdict

from aiohttp_apispec import docs, request_schema
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPConflict,
    HTTPMethodNotAllowed,
)

from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response
from app.db.game.models import (
    Player, 
    PlayerSession
)
from app.web.bot.schemes import (
    PlayerSchema,
    PlayerSessionSchema,
)

class PlayerHitView(AuthRequiredMixin, View):
    pass

class PlayerStandView(AuthRequiredMixin, View):
    pass
