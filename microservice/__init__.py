# Main microservice script
# Retrieves, configures and connects all of the
# components of the microservice

import argparse

import os

from flask import Flask
from flask_cors import CORS

from .config import config, config_logging

def create_app(args=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # add user provided configurations for the
    if args:
        app.config.update(
            MODEL_PATH=args.model_path,
            MODEL_FORMAT=args.model_format,
            MODEL_LANGUAGE=args.model_language
        )

    # setup the app configuration
    if os.getenv('FLASK_ENV') == 'production':
        app.config.from_object(config.ProductionConfig)
    elif os.getenv('FLASK_ENV') == 'development':
        app.config.from_object(config.DevelopmentConfig)
    elif os.getenv('FLASK_ENV') == 'testing':
        app.config.from_object(config.TestingConfig)

    # setup the cors configurations
    if app.config['CORS']['origins']:
        CORS(app, origins=app.config['CORS']['origins'])

    with app.app_context():
        # add logger configuration
        config_logging.init_app(app)

        # add document query routes
        from .routes.embeddings import embeddings
        app.register_blueprint(embeddings.bp)

    # add error handlers
    from .routes.general import error_handlers
    error_handlers.register(app)

    # TODO: log start of the service
    # return the app
    return app