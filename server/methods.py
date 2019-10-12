import tensorflow as tf
import numpy as np
from models.GE2E.lstmp import LSTMP
from pyasv.speech import FilterBank
from scipy.spatial.distance import cosine, cdist

def init(config):
    sess = tf.Session()
    INPUT = tf.placeholder(shape=[None, 251, 64], dtype=tf.float32, name="x")
    MODEL = LSTMP(config, layer_num=3, lstm_units=400)
    opt = MODEL.inference(tf.transpose(INPUT, [1, 0 ,2]))
    saver = tf.train.Saver()
    saver.restore(sess, "models/checkpoint/ge2e-new.ckpt")
    return INPUT, opt, sess

def enroll(path, name, config, sess, opt, inp, dic):
    ext = FilterBank("", config)
    fbank = ext._extract_one(path, n_fft=512, n_mels=64, sample_rate=16000, length=16000 * 8)
    assert isinstance(sess, tf.Session)
    data = sess.run(opt, feed_dict={inp: fbank.reshape(-1, 251, 64)})
    print(data.shape)
    if name not in dic.keys():
        dic[name] = [data[-1]]
    else:
        print(name)
        dic[name].append(data[-1])

def test(path, config, sess, opt, inp, dic):
    ext = FilterBank("", config)
    fbank = ext._extract_one(path, n_fft=512, n_mels=64, sample_rate=16000, length=16000 * 8)
    assert isinstance(sess, tf.Session)
    data = sess.run(opt, feed_dict={inp: fbank.reshape(-1, 251, 64)})
    score = -1
    res = ""
    ss = []
    print("data shape", data.shape)
    for key in dic.keys():
        s = 1 - cosine(data[-1], np.mean(np.array(dic[key]), axis=0))
        ss.append((key, s))
        if score < s:
            score = s
            res = key
    print(ss)
    return res

