from common.db.gino_instance import gino_instance as db


class GameChat(db.Model):
    __tablename__ = "game_chats"

    chat_id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.Unicode, nullable=True)