import json

from aiohttp_apispec import docs, request_schema
from aiohttp_session import new_session
from aiohttp.web_exceptions import HTTPForbidden

from admin_app.base_utils import View
from admin_app.web.mixins import AuthRequiredMixin
from admin_app.web.utils import json_response
from admin_app.auth.schemes.admin import AdminSchema


class AdminIndexView(View):
    async def get(self):
        return json_response()


class AdminLoginView(View):
    @docs(
        tags=["admin"],
        summary="Log in admin",
        description="Log in a registered admin with email and password",
        responses={
            200: {"description": "Logged in", "schema": AdminSchema},
            403: {"description": "Invalid password or email"},
        },
    )
    @request_schema(AdminSchema)
    async def post(self):
        email = self.data["email"]
        password = self.data["password"]
        
        admin = await self.store.admins.get_by_email(email)
        if admin is None or \
            not admin.is_password_valid(password):
            raise HTTPForbidden(
                reason="invalid password or email", 
                text=json.dumps({ "email": email, "password": password })
            )

        session = await new_session(request=self.request)
        session["admin"] = AdminSchema().dump(admin)

        return json_response(data=AdminSchema(exclude=["password"]).dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"],
        summary="Show current admin",
        description="Show current session logged in admin",
        responses={
            200: {"description": "Current admin", "schema": AdminSchema},
            401: {"description": "Unauthorized"},
            403: {"description": "Invalid credentials"},
        },
    )
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
