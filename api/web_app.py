import logging
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_rest_jsonapi_next import Api, ResourceDetail, ResourceList
from sqlalchemy_utils.functions import database_exists

logger = logging.getLogger()
app = Flask(__name__)
app.config['DEBUG'] = True
DBNAME = 'smartmeters'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DBNAME}.db'
db = SQLAlchemy(app)
DTSU666 = 'DTSU666'

def get_db():
    return db

from api.smart_meter import SmartMeter, SmartMeterSchema

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

        sm1 = SmartMeter(em_Type=DTSU666, em_Status='OK', sniffing_quality='0')
        db.session.add(sm1)
        db.session.commit()


def setup_webapp_api():
    logger.info("setup_webapp_api starting")
    setup_database()

    started = datetime.now().strftime("%Y/%m/%d/ %H:%M:%S")
    @app.route('/info')
    def info():
        return f'{"app":"Modbus Sniffer", "ver":"1.0.1", run:{started}}'

    api = Api(app)
    api.route(SmartMetersMany, 'smartmeter_many', '/smartmeters')
    api.route(SmartMeterOne, 'smartmeter_one', '/smartmeters/<int:id>')
    
    logger.info("setup_webapp_api finished")


def update_statistics(queries_amount):
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(em_Type=DTSU666)).one()
        sm[0].em_RdTime = datetime.now().strftime("%Y/%m/%d/ %H:%M:%S.%f")
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
