import ipaddress
import logging
import uuid
from functools import wraps

import sentry_sdk
from flask import Flask, abort, request, jsonify
from flask.json import JSONEncoder
from sentry_sdk.integrations.flask import FlaskIntegration

from ip_analyzer.ip_storage.factory import create_storage
from ip_analyzer.rate_limiter.limiter_factory import create_rate_limiter
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


init_app()
rate_limiter = create_rate_limiter()
ip2country_db = create_storage()


def rate_limit_middleware():
    def _rate_limit_middleware(f):
        @wraps(f)
        def __rate_limit_middleware(*args, **kwargs):
            try:
                req_ip = request.remote_addr
                if not rate_limiter.can_be_served(req_ip):
                    return jsonify({
                        "message": "Rate limit has reached",
                        "data": None,
                        "error": "RATE LIMIT"
                    }), 429
            except Exception as e:
                return jsonify({
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(e)
                }), 500
            return f(*args, **kwargs)

        return __rate_limit_middleware

    return _rate_limit_middleware


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
@rate_limit_middleware()
def get_ip_country():
    requested_ip = request.args.get("ip")

    if not requested_ip:
        return jsonify({
            "message": "missing 'ip' query param",
            "data": None,
            "error": "BAD REQUEST"
        }), 400

    try:
        ipaddress.ip_address(requested_ip)
    except ValueError as ve:
        return jsonify({
            "message": "%s does not appear to be an IPv4 or IPv6 address" % requested_ip,
            "data": requested_ip,
            "error": "BAD REQUEST"
        }), 400

    ip_data = ip2country_db.get_country(requested_ip)
    if ip_data is None:
        return jsonify({
            "message": "%s is unknown" % requested_ip,
            "data": requested_ip,
            "error": "NOT FOUNT"
        }), 404

    return jsonify({
        "country": ip_data.country,
        "city": ip_data.city
    }), 200


# Only for develop!
if __name__ == '__main__':
    logging.info('Staring development server on port %d', LISTEN_PORT)
    app.run(host='0.0.0.0', port=LISTEN_PORT)
