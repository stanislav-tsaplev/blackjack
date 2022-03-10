from sqlalchemy.dialects.postgresql import JSON

from app.db.core.gino import gino_orm as db


class PlayerDataport(db.Model):
    __tablename__ = "player_dataports"

    player_session_id = db.Column(db.Integer, 
        db.ForeignKey("player_sessions.id", ondelete="CASCADE"),
        primary_key=True)

    request_data = db.Column(JSON, nullable=True)
    response_data = db.Column(JSON, nullable=True)