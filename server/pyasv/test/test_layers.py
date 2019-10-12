import sys
sys.path.append("../..")
import pytest
import tensorflow as tf
import numpy as np
from numpy.testing import *
from pyasv.basic import layers

class TestTDNN(object):
    def test_tdnn_valid(self):
        with tf.Session() as sess:
            x = tf.ones([ 4., 5., 4.])
            op_1 = layers.t_dnn(x, length=2, padding='VALID', strides=1, name="t_dnn")
            op_2 = layers.t_dnn(op_1, length=2, strides=1, name="t_dnn_2")
            sess.run(tf.global_variables_initializer())
            res = sess.run(op_2)
            assert list(res.shape) == [4, 3 ,4]
            b = np.full([4, 3, 4], fill_value=64.0)
            assert_array_equal(res, b)

    def test_tdnn_except(self):
        with pytest.raises(ValueError) as e:
            x = tf.ones([ 4, 5, 4])
            op_1 = layers.t_dnn(x, length=2, padding='VALID', strides=1, name="t_dnn")

class TestStatisticsPooling(object):
    def test_normal(self):
        x = np.array([ [ [2., 3., 4.],
                         [6., 3., 3.],
                         [1., 9., 5.]],

                       [ [3., 4., 5.],
                         [4., 4., 4.],
                         [11., 7., 9.]]])
        x1, x2, x3 = np.std([2., 6., 1.]), np.std([3., 3., 9.]), np.std([4., 3., 5.])
        x4, x5, x6 = np.std([3., 4., 11.]), np.std([4., 4., 7.]), np.std([5., 4., 9.])
        y = np.array([ [3., 5., 4., x1, x2, x3],
                       [6., 5., 6., x4, x5, x6] ])
        x = tf.constant(x)
        sess = tf.Session()
        op = layers.static_pooling(x)
        y_ = sess.run(op)
        assert list(y_.shape) == [2, 6]
        assert_array_equal(y, y_)

    def test_exception(self):
        with pytest.raises(ValueError):
            x = tf.ones([2,3,3,3])
            layers.static_pooling(x)