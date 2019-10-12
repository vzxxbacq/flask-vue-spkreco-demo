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


config = Config("lstmp.yaml")

INP, OPT, SESS = methods.init(config)

SPKR = data.Speakers('spkr.pkl', 'vector.npy')

root = 'wav'

wav = [os.path.join(root, i) for i in os.listdir(root)]
"""
for i in wav:
    name = i.split("/")[-1].split("_")[0]
    if name != 'test':
        methods.enroll(i, name, config, SESS, OPT, INP, SPKR.vectors)

SPKR.dump()
SPKR.update_vector_file()
"""
print(methods.test("wav/test_09-01-2019-19-09-01.wav", config, SESS, OPT, INP, SPKR.vectors))
print(methods.test("wav/test_09-01-2019-19-01-16.wav", config, SESS, OPT, INP, SPKR.vectors))
