from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from app.db.core.gino import gino_orm as db


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    def is_password_valid(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        if session is None:
            return None

        return cls(
            id=session["admin"]["id"], 
            email=session["admin"]["email"]
        )

    @classmethod
    def from_gino_model(cls, model: Optional["AdminModel"]) -> Optional["Admin"]:
        if model is None:
            return None
            
        return cls(
            id=model.id, 
            email=model.email, 
            password=model.password
        )


class AdminModel(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String())
    password = db.Column(db.String(), nullable=True)