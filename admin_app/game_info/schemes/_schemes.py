from marshmallow import Schema, fields


class UserSchema(Schema):
    class Meta:
        ordered = True
    
    vk_id = fields.Int(required=True)
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    city = fields.Str(required=False)


class PlayerSchema(Schema):
    class Meta:
        ordered = True
    
    vk_id = fields.Int(required=True)
    chat_id = fields.Int(required=True)
    money = fields.Int(required=True)
    

class GameChatSchema(Schema):
    class Meta:
        ordered = True
    
    chat_id = fields.Int(required=True)
    name = fields.Str(required=False)


class GameSessionSchema(Schema):
    class Meta:
        ordered = True
    
    id = fields.Int(required=False)
    chat_id = fields.Int(required=True)
    started_at = fields.DateTime(required=True)
    closed_at = fields.DateTime(required=False)
    state = fields.Int(required=True)

    players = fields.Nested("PlayerSessionSchema", many=True, required=True)


class PlayerSessionSchema(Schema):
    class Meta:
        ordered = True
        
    vk_id = fields.Int(required=True)
    session_id = fields.Int(required=True)
    gain = fields.Int(required=False)    
