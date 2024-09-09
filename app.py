import os
from flask import *
from conf import dbinfo
from models.sqlmodel import db
from utils import uuidGen
from routes import mainBluePrint
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    try:
        db_uri = f"mysql+pymysql://{dbinfo['username']}:{dbinfo['password']}@" \
                 f"{dbinfo['server']}:{dbinfo['port']}/{dbinfo['dbname']}"
        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SECRET_KEY'] = uuidGen()
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        raise
    db.init_app(app)
    app.register_blueprint(mainBluePrint)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)