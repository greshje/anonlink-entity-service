import pathlib
import uuid
import connexion
from flask import g, request
import structlog
from tenacity import RetryError

from backend.entityservice.logger_setup import setup_logging

import backend.entityservice.views
from backend.entityservice.tracing import initialize_tracer
import opentracing
from flask_opentracing import FlaskTracing
from backend.entityservice import database as db
from backend.entityservice.serialization import generate_scores
from backend.entityservice.object_store import connect_to_object_store
from backend.entityservice.settings import Config as Config
from backend.entityservice.utils import fmt_bytes, iterable_to_stream

# Logging setup
setup_logging()

# Define the WSGI application object
# Note we explicitly do this before importing our own code
con_app = connexion.FlaskApp(__name__, specification_dir='api_def', debug=True)
app = con_app.app

con_app.add_api(pathlib.Path("openapi.yaml"),
                base_path='/',
                options={'swagger_ui': False},
                strict_validation=Config.CONNEXION_STRICT_VALIDATION,
                validate_responses=Config.CONNEXION_RESPONSE_VALIDATION)


# Config could be Config, DevelopmentConfig or ProductionConfig
app.config.from_object(Config)

logger = structlog.wrap_logger(app.logger)
# Tracer setup (currently just trace all requests)
flask_tracer = FlaskTracing(initialize_tracer, True, app)


@app.before_first_request
def before_first_request():
    db_min_connections = Config.FLASK_DB_MIN_CONNECTIONS
    db_max_connections = Config.FLASK_DB_MAX_CONNECTIONS
    try:
        db.init_db_pool(db_min_connections, db_max_connections)
    except RetryError:
        logger.error("Giving up on connecting to database")
        raise SystemExit("Couldn't establish connection to database pool")


@app.before_request
def before_request():
    g.log = logger.new(request=str(uuid.uuid4())[:8])
    if Config.LOG_HTTP_HEADER_FIELDS is not None:
        headers = {}
        for header in Config.LOG_HTTP_HEADER_FIELDS.split(','):
            header = header.strip()
            if header in request.headers:
                headers[header] = request.headers[header]
        g.log.bind(**headers)
    g.flask_tracer = flask_tracer


if __name__ == '__main__':
    con_app.run(debug=True, port=8000)
