import logging
import uuid

import sentry_sdk
from flask import Flask, abort, request, jsonify
from flask.json import JSONEncoder
from sentry_sdk.integrations.flask import FlaskIntegration

from settings import LISTEN_PORT, SENTRY_DSN, ENVIRONMENT

sentry_sdk.init(dsn=SENTRY_DSN, environment=ENVIRONMENT, integrations=[FlaskIntegration()])


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


app = Flask(__name__)
process_id = str(uuid.uuid1())


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s]" +
                                  "[" + ENVIRONMENT + "]" +
                                  "[ip2Country]" +
                                  "[" + process_id + "]" +
                                  "[%(levelname)s]" +
                                  " %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def init_app():
    setup_logger()
    logging.info('Starting app... ID: %s', process_id)
    app.json_encoder = CustomJSONEncoder


@app.errorhandler(400)
def resource_not_found(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(405)
def resource_not_found(e):
    return jsonify(error=str(e)), 405


@app.route('/health', methods=['GET'])
def health_check():
    # TODO: Check the ip analyzer

    logging.debug("I'm alive!")
    return jsonify({'status': 'ok'})


@app.route('/v1/find-country', methods=['GET'])
def get_ip_country():
    pass


init_app()

# Only for develop!
if __name__ == '__main__':
    logging.info('Staring development server on port %d', LISTEN_PORT)
    app.run(host='0.0.0.0', port=LISTEN_PORT)
