import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_rest_jsonapi_next import Api, ResourceDetail, ResourceList
from sqlalchemy_utils.functions import database_exists

logger = logging.getLogger()
app = Flask(__name__)
app.config['DEBUG'] = True
APPNAME= 'ModbusSniffer'
APPVER= '1.0.1'
DBNAME = 'modbussniffer'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DBNAME}.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///:memory:'
db = SQLAlchemy(app)
DTSU666 = 'DTSU666'

def get_db():
    return db

from api.Info import Info, InfoSchema
from api.SmartMeter import SmartMeter, SmartMeterSchema

class InfosMany(ResourceList):
    schema = InfoSchema
    data_layer = {'session': db.session,
                  'model': Info}
class InfoOne(ResourceDetail):
    schema = InfoSchema
    data_layer = {'session': db.session,
                  'model': Info}

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

def setup_database(started):
    with app.app_context():
        db.create_all()

        info1 = Info(app_name=APPNAME, app_ver=APPVER, app_started=started)
        db.session.add(info1)

        sm1 = SmartMeter(em_Type=DTSU666, em_Status='OK', em_SniffingRate='0')
        db.session.add(sm1)
        db.session.commit()
def init_file_database(started):
    # set it net to imports:
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DBNAME}.db'
    if database_exists(f'sqlite:///instance/{DBNAME}.db'):
        update_app_info_started(started)
    else:
        setup_database(started)

def init_inmemory_database(started):
    # set it net to imports:
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///:memory:'
    setup_database(started)

def setup_webapp_api(inmemory: bool):
    logger.warning("setup_webapp_api starting")
    started = datetime.now().strftime("%Y/%m/%d/ %H:%M:%S")
    if inmemory:
        init_file_database(started)
    else:
        init_inmemory_database(started)

    # @app.route('/info')
    # def info():
    #     return f'{"app":"Modbus Sniffer", "ver":"1.0.1", run:{started}}'

    api = Api(app)
    api.route(InfosMany, 'info_many', '/infos')
    api.route(InfoOne, 'info_one', '/infos/<int:id>')
    api.route(SmartMetersMany, 'smartmeter_many', '/smartmeters')
    api.route(SmartMeterOne, 'smartmeter_one', '/smartmeters/<int:id>')
    
    logger.info("setup_webapp_api finished")

def update_app_info_started(started):
    logger.debug(f'update_app_info_started: for date:{started}')
    with app.app_context():
        inf = db.session.execute(
            db.select(Info).filter_by(app_name=APPNAME)).one()
        inf[0].app_started = started
        db.session.commit()

#sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) cannot commit - no transaction is active
#(Background on this error at: https://sqlalche.me/e/14/e3q8)

def update_smart_meter(dictData):
    logger.debug(f'update_smart_meter:{dictData}')
    with app.app_context():
        sm = db.session.execute(
            db.select(SmartMeter).filter_by(em_Type=DTSU666)).one()
        entry = sm[0]
        for name, value in iter(dictData.items()):
            setattr(entry, name, value)
        db.session.commit()
