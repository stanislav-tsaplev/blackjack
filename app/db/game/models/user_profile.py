from app.db.core.gino import gino_orm as db


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    vk_id = db.Column(db.Integer, unique=True, primary_key=True)
    first_name = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    city = db.Column(db.Unicode, nullable=True)
    
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self._players = list()

    # @property
    # def players(self):
    #     return self._players

    # @players.setter
    # def add_player(self, player):
    #     self._players.append(player)