from app.db.core.gino import gino_orm as db
from app.bot.utils.playcards import CardRank, CardSuit


class CardDeal(db.Model):
    __tablename__ = "card_deals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_session_id = db.Column(db.Integer, 
        db.ForeignKey("player_sessions.id", ondelete="CASCADE"))
    card_rank = db.Column(db.Enum(CardRank), nullable=False)
    card_suit = db.Column(db.Enum(CardSuit), nullable=False)