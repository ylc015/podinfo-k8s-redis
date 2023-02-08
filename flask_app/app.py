from flask import Flask
from werkzeug.exceptions import HTTPException
import redis
import os
import json
from flask import request

app = Flask(__name__)

APP_READY_KEY = "app_ready_key"


@app.route("/healthz")
def health():
    return { "status": "OK" }


@app.route("/readyz")
def ready():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    is_ready = int(r.get(APP_READY_KEY)) == 1
    print(f"after set {is_ready}")
    if not is_ready:
        return  { "status": "SERVICE UNAVAILABLE" }
    return { "status": "OK" }

@app.route("/readyz/enable")
def enable_traffic():
    # ping redis here
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set(APP_READY_KEY, 1)
    return {}, 202

@app.route("/readyz/disable")
def disable_traffic():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set(APP_READY_KEY, 0)
    return {}, 202

@app.route("/env")
def get_env_json():
    return json.dumps(dict(os.environ)), 200


@app.route("/headers")
def get_request_headers():
    return dict(request.headers)