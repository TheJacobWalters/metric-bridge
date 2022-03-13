from flask import Flask
from flask import request
from base64 import b64decode as b64d
import requests
import socket
import logging
app = Flask(__name__)

# this will have the form ?service=<service>namespace=<namespace>port=<port>protocol=<http or tcp>
# the following url has the ? and the & escaped
# curl localhost:25000/lookup\?service=node-exporter\&namespace=default\&port=9100\&protocol=http\&schema=http
# curl localhost:25000/lookup\?service=kube-dns\&namespace=kube-system\&port=53\&protocol=tcp
# this will need to pass if a 403 forbidden is there
# this will need to mount a service accoutn that can authenticate with the apiserver


@app.route("/lookup")
def hello():
    lookups = ["service", "namespace", "port", "protocol", "schema", "health_endpoint"]

    # this could have Nones in here
    params = {x: request.args.get(x) for x in lookups}
    if params["health_endpoint"] == None:
        params["health_endpoint"] = ""

    res = None
    authorization = request.headers.get('Authorization')
    if authorization is not None:
        username, password = b64d(authorization.split(' ')[1]).decode().split(":")
    def handle_http():
        if not all (params):
            raise Exception
        host = f"{params['schema']}://" + base_host + f":{params['port']}/{params['health_endpoint']}"
        headers = {}
        if request.headers.get("Authorization") is not None:
            headers['Authorization'] = request.headers.get("Authorization")
        res = requests.get(host, verify=False, headers=headers)
        if res.status_code not in [200, 304]:
            raise Exception

    def handle_tcp():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((base_host, int(params["port"])))

    # the service name and namespace plus the ending will always be in the dns record
    try:
        base_host = f"{params['service']}.{params['namespace']}.svc.cluster.local"
    except:
        return "", 500
    try:
        if params["protocol"] in ["http", "https"]:
            handle_http()
        elif params["protocol"] == "tcp":
            handle_tcp()
    except Exception as e:
        logging.error(e)
        return "", 500

    return "", 200


if __name__ == "__main__":
    app.run()
