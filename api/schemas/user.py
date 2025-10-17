from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))

class UserRegisterSchema(UserSchema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))