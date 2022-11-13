import logging
import threading
import time

from common.smartLogger import setup_logger

setup_logger(__package__)

import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from serial_snooper import SerialSnooper

logger = logging.getLogger()
app = Flask(__name__)
    
def setup_app():
    logger.info("setup_app starting")
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////artists.db'
        db = SQLAlchemy(app)
        class Artist(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String)
            birth_year = db.Column(db.Integer)
            genre = db.Column(db.String)
        db.create_all()

        from marshmallow_jsonapi.flask import Schema
        from marshmallow_jsonapi import fields

        # Create data abstraction layer
        class ArtistSchema(Schema):
            class Meta:
                type_ = 'artist'
                self_view = 'artist_one'
                self_view_kwargs = {'id': '<id>'}
                self_view_many = 'artist_many'

            id = fields.Integer()
            name = fields.Str(required=True)
            birth_year = fields.Integer(load_only=True)
            genre = fields.Str()

        app.route('/')
        def example():
            return '{"name":"zzzz"}'
            # return f'{"name":"{serialSnooper.get_statistics()}"}'
        logger.info("setup_app finished") 
        return app

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

    app = setup_app()
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
