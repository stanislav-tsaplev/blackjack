from common.db.gino_instance import gino_instance as db


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    vk_id = db.Column(db.Integer, unique=True, primary_key=True)
    first_name = db.Column(db.Unicode)
    last_name = db.Column(db.Unicode)
    city = db.Column(db.Unicode, nullable=True)
