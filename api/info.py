from sqlalchemy import Column, Integer, String
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from api.web_app import get_db

class Info(get_db().Model):
    id = Column(Integer, primary_key=True)
    app_name = Column(String)
    app_ver = Column(String)
    app_started = Column(String)
    
# Create data abstraction layer

class InfoSchema(Schema):
    class Meta:
        type_ = 'info'
        self_view = 'info_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'info_many'

    id = fields.Integer()
    app_name = fields.Str(required=True)
    app_ver = fields.Str(required=True)
    app_started = fields.Str(required=True)
# Create resource managers and endpoints
