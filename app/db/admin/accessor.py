import typing
from typing import Optional
from hashlib import sha256

from app.db.base.accessor import BaseAccessor
from app.db.admin.models import Admin, AdminModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await super().connect(app)

        default_admin = await self.get_by_email(app.config.admin.email)
        if default_admin is None:
            await self.create_admin(
                email=app.config.admin.email, 
                password=app.config.admin.password
            )

    async def get_by_email(self, email: str) -> Optional[Admin]:
        admin = await AdminModel.query.where(AdminModel.email == email).gino.one_or_none()
        return Admin.from_gino_model(admin)

    async def get_by_id(self, id: int) -> Optional[Admin]:
        admin = await AdminModel.get(id)
        return Admin.from_gino_model(admin)

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = await AdminModel.create(
            email=email,
            password=sha256(password.encode()).hexdigest()
        )
        return Admin.from_gino_model(admin)
