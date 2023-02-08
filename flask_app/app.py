from flask import Flask
from werkzeug.exceptions import HTTPException
import redis
import os
import json
from flask import request
import asyncio


app = Flask(__name__)

APP_READY_KEY = "app_ready_key"
REDIS_HOST = os.environ.get("REDIS_HOST", 'localhost')
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)


@app.route("/healthz")
def health():
    return { "status": "OK" }


@app.route("/readyz")
def ready():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    is_ready = int(r.get(APP_READY_KEY)) == 1
    print(f"after set {is_ready}")
    if not is_ready:
        return  { "status": "SERVICE UNAVAILABLE" }
    return { "status": "OK" }

@app.route("/readyz/enable")
def enable_traffic():
    # ping redis here
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    r.set(APP_READY_KEY, 1)
    return {}, 202

@app.route("/readyz/disable")
def disable_traffic():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    r.set(APP_READY_KEY, 0)
    return {}, 202

@app.route("/env")
def get_env_json():
    return json.dumps(dict(os.environ)), 200

@app.route("/headers")
def get_request_headers():
    return dict(request.headers)

@app.route("/delay/<seconds>")
async def delay_request(seconds):
    try: 
        await asyncio.sleep(int(seconds))
    except: print(f"Invalid input {seconds}")
    return {"delay": seconds}

# TODO handle redis offline error
@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    return {"code": 400, "message": "Redis is offline"}


@app.route("/cache/<key>", methods=["GET", "POST", "PUT", "DELETE"])
def cache(key: str):
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset="utf-8", decode_responses=True)
    if request.method == "GET":
        data = str(r.get(key))
        if data == 'None':
            return {}, 202
        try: 
            return dict(data)
        except:
            return data
    elif request.method == "DELETE":
        print(f"delete request {key}")
        r.delete(key)
    else:
        print(f"update {key} with {request.get_data()}")
        # POST or PUT
        r.set(key, request.data)

    return {}, 202
