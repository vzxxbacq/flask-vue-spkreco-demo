#!/usr/bin/env python3
import uuid
import data
from datetime import datetime
import os
import logger
import methods
from flask import Flask, jsonify, request
from flask_cors import CORS
from pyasv.config import Config

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

log = logger.init_logger(__name__)

config = Config("lstmp.yaml")

INP, OPT, SESS = methods.init(config)

SPKR = data.Speakers(info_path='spkr.pkl', vec_path='vector.npy')

@app.route('/server/options', methods=['GET', 'POST'])
def options():
    data = SPKR.to_options()
    print(data)
    return jsonify(data)


# sanity check route
@app.route('/server/ping', methods=['GET'])
def ping_pong():
    data = {'msg': 'pong!', 'bool': True}
    return jsonify(data)


@app.route('/server/spkr_list', methods=['POST'])
def spkr_list():
    data = SPKR.to_table()
    return jsonify({'table': data})


@app.route("/server/upload_enroll", methods=['POST'])
def meta():
    name =  request.form.get("name")
    try:
        os.mkdir('wav')
    except:
        pass
    now = datetime.now()
    SPKR.add({'name': name, 'date': now.strftime("%Y-%m-%d %H-%M-%S")})
    f = request.files['file']
    f_name = "wav/%s_%s.wav" % (name, now.strftime("%m-%d-%Y-%H-%M-%S"))
    f.save(f_name)
    print(f)
    methods.enroll(f_name, name, config, SESS, OPT, INP, SPKR.vectors)
    SPKR.update_vector_file()
    return jsonify({'msg': 'Enroll to %s OK!'%name})

@app.route('/server/test_upload', methods=['POST'])
def upload_test():
    try:
        os.mkdir('wav')
    except:
        pass
    now = datetime.now()
    f = request.files['file']
    f_name = "wav/%s_%s.wav"%('test', now.strftime("%m-%d-%Y-%H-%M-%S"))
    f.save(f_name)
    res = methods.test(f_name, config, SESS, OPT, INP, SPKR.vectors)
    return jsonify({'msg': res})

@app.route('/server/delete', methods=['POST'])
def delete_spkr():
    name = request.form.get('name')
    print(request.form)
    SPKR.remove(name)
    return jsonify({'msg': "OK"})

if __name__ == '__main__':
    app.run()
