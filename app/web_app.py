import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from flask_rest_jsonapi_next import Api, ResourceDetail, ResourceList
from sqlalchemy_utils.functions import database_exists

logger = logging.getLogger()
app = Flask(__name__)
app.config['DEBUG'] = True
DBNAME = 'smartmeters'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DBNAME}.db'
db = SQLAlchemy(app)
DTSU666 = 'dtsu666'


class SmartMeter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sniffing_quality = db.Column(db.String)
    em_Uab = db.Column(db.String)
    em_Ubc = db.Column(db.String)
    em_Uca = db.Column(db.String)
    em_Ua = db.Column(db.String)
    em_Ub = db.Column(db.String)
    em_Uc = db.Column(db.String)
    em_ImpEp = db.Column(db.String)

# Create data abstraction layer


class SmartMeterSchema(Schema):
    class Meta:
        type_ = 'smartmeter'
        self_view = 'smartmeter_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'smartmeter_many'

    id = fields.Integer()
    name = fields.Str(required=True)
    sniffing_quality = fields.Str(required=True)
    em_Uab = fields.Str(required=False)
    em_Ubc = fields.Str(required=False)
    em_Uca = fields.Str(required=False)
    em_Ua = fields.Str(required=False)
    em_Ub = fields.Str(required=False)
    em_Uc = fields.Str(required=False)
    em_ImpEp = fields.Str(required=False)

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
    if database_exists(f'sqlite:///instance/{DBNAME}.db'):
        return

    with app.app_context():
        db.create_all()

        sm1 = SmartMeter(name=DTSU666, sniffing_quality='0')
        db.session.add(sm1)
        db.session.commit()


def setup_webapp_api():
    logger.info("setup_webapp_api starting")
    setup_database()

    api = Api(app)
    api.route(SmartMetersMany, 'smartmeter_many', '/smartmeters')
    api.route(SmartMeterOne, 'smartmeter_one', '/smartmeters/<int:id>')

    @app.route('/')
    def example():
        return '{"app":"SmartMeter Sniffer"}'
    logger.info("setup_webapp_api finished")


def update_sniffing_quality(value):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(name=DTSU666)).one()
        sm[0].sniffing_quality = value
        db.session.commit()


def update_electricity(dictData):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(name=DTSU666)).one()
        for name, value in iter(dictData.items()):
            if name == 'Uab':
                sm[0].em_Uab = value
            elif name == 'Ubc':
                sm[0].em_Ubc = value
            elif name == 'Uca':
                sm[0].em_Uca = value
            elif name == 'Ua':
                sm[0].em_Ua = value
            elif name == 'Ub':
                sm[0].em_Ub = value
            elif name == 'Uc':
                sm[0].em_Uc = value
        db.session.commit()

def update_power(dictData):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(name=DTSU666)).one()
        for name, value in iter(dictData.items()):
            if name == 'ImpEp':
                sm[0].em_ImpEp = value
        db.session.commit()