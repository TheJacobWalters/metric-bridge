from flask import Flask
from flask import request
import requests
import socket
app = Flask(__name__)

# this will have the form ?service=<service>namespace=<namespace>port=<port>protocol=<http or tcp>
# the following url has the ? and the & escaped
# curl localhost:25000/lookup\?service=node-exporter\&namespace=default\&port=9100\&protocol=http\&schema=http
# curl localhost:25000/lookup\?service=kube-dns\&namespace=kube-system\&port=53\&protocol=tcp
# this will need to pass if a 403 forbidden is there
# this will need to mount a service accoutn that can authenticate with the apiserver


@app.route("/lookup")
def hello():
    lookups = ["service", "namespace", "port", "protocol", "schema"]
    
    # this could have Nones in here
    params = {x : request.args.get(x) for x in lookups }

    res = None

    try :
        base_host = f"{params['service']}.{params['namespace']}.svc.cluster.local"
        if params['protocol'] in ["http", "https"] and all(params):
            host = f"{params['schema']}://" + base_host + f":{params['port']}"
            res = requests.get(host, verify=False)
            
        elif params['protocol'] == "tcp":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((base_host, int(params['port'])))
        else :
            raise Exception
    except :
        return "", 500
    return "", 200

if __name__ == "__main__":
    app.run()
