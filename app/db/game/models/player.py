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
    
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self._player_sessions = list()

    # @property
    # def player_sessions(self):
    #     return self._player_sessions

    # @player_sessions.setter
    # def add_player_session(self, player_session):
    #     self._player_sessions.append(player_session)
