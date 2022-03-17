from marshmallow import Schema, fields


class PlayerInfoSchema(Schema):
    class Meta:
        ordered = True
        
    vk_id = fields.Int(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    city = fields.Str(required=False)
    bet = fields.Int(required=True)
    gain = fields.Int(required=True)


class GameInfoSchema(Schema):
    class Meta:
        ordered = True
        
    chat_id = fields.Int(required=True)
    chat_name = fields.Str(required=False)
    started_at = fields.DateTime(required=True)
    closed_at = fields.DateTime(required=True)
    players = fields.Nested(PlayerInfoSchema, many=True, required=True)


class GameSummarySchema(Schema):
    class Meta:
        ordered = True
        
    total = fields.Int(required=True)
    games = fields.Nested(GameInfoSchema, many=True, required=True)


class PaginationQuerystringSchema(Schema):
    offset = fields.Int(required=False)
    limit = fields.Int(required=False)
