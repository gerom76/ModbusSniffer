import logging
import threading
import time

from common.smartLogger import setup_logger

setup_logger(__package__)

import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from flask_rest_jsonapi_next import Api, ResourceDetail, ResourceList

from serial_snooper import SerialSnooper

logger = logging.getLogger()
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartmeters.db'
db = SQLAlchemy(app)
class SmartMeter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    value = db.Column(db.String)

def setup_database(db):
    with app.app_context():
        db.create_all()

        sm1 = SmartMeter(name='dtsu666', value='0')
        db.session.add(sm1)
        db.session.commit()
        
def setup_webapp_api():
    logger.info("setup_webapp_api starting")

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

    api = Api(app)
    api.route(SmartMetersMany, 'smartmeter_many', '/smartmeters')
    api.route(SmartMeterOne, 'smartmeter_one', '/smartmeters/<int:id>')


    @app.route('/')
    def example():
        return '{"name":"zzzz"}'
        # return f'{"name":"{serialSnooper.get_statistics()}"}'
    logger.info("setup_webapp_api finished") 

def run_webserver(app: any):
    logger.info("Web server thread starting")
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    logger.info("Web server thread finishing")

def run_sniffer(serialSnooper: SerialSnooper, port, baud):
    logger.info(f"Starting sniffing for port:{port} baud:{baud}")
    while True:
        data = serialSnooper.read_raw(16)
        if len(data):
        #     logger.debug(data)
            serialSnooper.process(data)
            logger.info(f"Statistics: {serialSnooper.get_statistics()}")
        # sleep(float(1)/ss.baud)
    logger.info("Sniffer thread  finishing")

if __name__ == "__main__":
    logger.debug("__main__.Begin")
    baud = 9600
    try:
        port = sys.argv[1]
    except IndexError:
        print("Usage: python3 {} device [baudrate, default={}]".format(
            sys.argv[0], baud))
        sys.exit(-1)
    try:
        baud = int(sys.argv[2])
    except (IndexError, ValueError):
        pass

    setup_database(db)
    setup_webapp_api()
    # sys.exit(0)
    ss = SerialSnooper(port, baud)

    web_server_thread = threading.Thread(target=run_webserver, args=(app,), daemon=True)
    sniffer_thread = threading.Thread(target=run_sniffer, args=(ss, port, baud,), daemon=True)

    logger.info("Starting threads")
    web_server_thread.start()
    time.sleep(1)
    sniffer_thread.start()

    web_server_thread.join()
    sniffer_thread.join()

    logger.info("Finished threads")
    sys.exit(0)
