from marshmallow import Schema, fields


class PlayerSchema(Schema):
    vk_id = fields.Int(required=True)
    bet = fields.Int(required=True)
    gain = fields.Int(required=True)


class GameSchema(Schema):
    chat_id = fields.Int(required=True)
    started_at = fields.DateTime(required=True)
    closed_at = fields.DateTime(required=True)
    players = fields.Nested(PlayerSchema, many=True, required=True)


class GameListSchema(Schema):
    total = fields.Int(required=False)
    games = fields.Nested(GameSchema, many=True, required=True)