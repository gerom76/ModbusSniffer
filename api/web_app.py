import logging
from datetime import datetime

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
    sniffing_quality = db.Column(db.String)
    em_Type = db.Column(db.String)
    em_Status = db.Column(db.String)
    em_RdTime = db.Column(db.String)
    em_Queries = db.Column(db.String)
    em_Uab = db.Column(db.String)
    em_Ubc = db.Column(db.String)
    em_Uca = db.Column(db.String)
    em_Ua = db.Column(db.String)
    em_Ub = db.Column(db.String)
    em_Uc = db.Column(db.String)
    em_Ia = db.Column(db.String)
    em_Ib = db.Column(db.String)
    em_Ic = db.Column(db.String)
    em_Pt = db.Column(db.String)
    em_Pa = db.Column(db.String)
    em_Pb = db.Column(db.String)
    em_Pc = db.Column(db.String)
    em_Qt = db.Column(db.String)
    em_Qa = db.Column(db.String)
    em_Qb = db.Column(db.String)
    em_Qc = db.Column(db.String)
    em_PFt = db.Column(db.String)
    em_PFa = db.Column(db.String)
    em_PFb = db.Column(db.String)
    em_PFc = db.Column(db.String)
    em_Freq = db.Column(db.String)

    em_ImpEp = db.Column(db.String)
    em_ExpEp = db.Column(db.String)
    em_Q1Eq = db.Column(db.String)
    em_Q2Eq = db.Column(db.String)
    em_Q3Eq = db.Column(db.String)
    em_Q4Eq = db.Column(db.String)
    
# Create data abstraction layer


class SmartMeterSchema(Schema):
    class Meta:
        type_ = 'smartmeter'
        self_view = 'smartmeter_one'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'smartmeter_many'

    id = fields.Integer()
    sniffing_quality = fields.Str(required=True)
    em_Type = fields.Str(required=True)
    em_Status = fields.Str(required=True)
    em_RdTime = fields.Str(required=False)
    em_Queries = fields.Str(required=False)
    em_Uab = fields.Str(required=False)
    em_Ubc = fields.Str(required=False)
    em_Uca = fields.Str(required=False)
    em_Ua = fields.Str(required=False)
    em_Ub = fields.Str(required=False)
    em_Uc = fields.Str(required=False)
    em_Ia = fields.Str(required=False)
    em_Ib = fields.Str(required=False)
    em_Ic = fields.Str(required=False)
    em_Pt = fields.Str(required=False)
    em_Pa = fields.Str(required=False)
    em_Pb = fields.Str(required=False)
    em_Pc = fields.Str(required=False)
    em_Qt = fields.Str(required=False)
    em_Qa = fields.Str(required=False)
    em_Qb = fields.Str(required=False)
    em_Qc = fields.Str(required=False)
    em_PFt = fields.Str(required=False)
    em_PFa = fields.Str(required=False)
    em_PFb = fields.Str(required=False)
    em_PFc = fields.Str(required=False)
    em_Freq = fields.Str(required=False)

    em_ImpEp = fields.Str(required=False)
    em_ExpEp = fields.Str(required=False)
    em_Q1Eq = fields.Str(required=False)
    em_Q2Eq = fields.Str(required=False)
    em_Q3Eq = fields.Str(required=False)
    em_Q4Eq = fields.Str(required=False)
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

        sm1 = SmartMeter(em_Type=DTSU666,  em_Status='OK', sniffing_quality='0' )
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


def update_statistics(queries_amount):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(em_Type=DTSU666)).one()
        sm[0].em_RdTime = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
        sm[0].em_Queries = queries_amount
        db.session.commit()

def update_sniffing_quality(value):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(em_Type=DTSU666)).one()
        sm[0].sniffing_quality = value
        db.session.commit()


def update_electricity(dictData):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(em_Type=DTSU666)).one()
        entry = sm[0]
        for name, value in iter(dictData.items()):
            setattr(entry, name, value)
        db.session.commit()


def update_power(dictData):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(em_Type=DTSU666)).one()
        entry = sm[0]
        for name, value in iter(dictData.items()):
            setattr(entry, name, value)
        db.session.commit()
