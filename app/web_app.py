import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from flask_rest_jsonapi_next import Api, ResourceDetail, ResourceList

logger = logging.getLogger()
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartmeters.db'
db = SQLAlchemy(app)

class SmartMeter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    value = db.Column(db.String)

# Create data abstraction layer
class SmartMeterSchema(Schema):
    class Meta:
        type_ = 'smartmeter'
        self_view = 'smartmeter_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'smartmeter_many'

    id = fields.Integer()
    name = fields.Str(required=True)

# Create resource managers and endpoints
class SmartMetersMany(ResourceList):
    schema = SmartMeterSchema
    data_layer = {'session': db.session,
                'model': SmartMeter}

class SmartMeterOne(ResourceDetail):
    schema = SmartMeterSchema
    data_layer = {'session': db.session,
                'model': SmartMeter}

def get_app():
    return app

def setup_database():
    with app.app_context():
        db.create_all()

        sm1 = SmartMeter(name='dtsu666', value='0')
        db.session.add(sm1)
        db.session.commit()
        
def setup_webapp_api():
    logger.info("setup_webapp_api starting")
    #setup_database()

    api = Api(app)
    api.route(SmartMetersMany, 'smartmeter_many', '/smartmeters')
    api.route(SmartMeterOne, 'smartmeter_one', '/smartmeters/<int:id>')

    @app.route('/')
    def example():
        return '{"app":"SmartMeter Sniffer"}'
    logger.info("setup_webapp_api finished") 
