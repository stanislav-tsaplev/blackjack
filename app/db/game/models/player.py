from app.db.core.gino import gino_orm as db


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vk_id = db.Column(db.Integer, 
                db.ForeignKey("user_profiles.vk_id", ondelete="CASCADE"))
    chat_id = db.Column(db.Integer, 
                db.ForeignKey("game_chats.chat_id", ondelete="CASCADE"))
    money = db.Column(db.Integer, default=0)

    secondary_key = db.Index("players_skey", "vk_id", "chat_id", unique=True)
    