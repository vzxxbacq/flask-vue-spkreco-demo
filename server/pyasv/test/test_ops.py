import sys
sys.path.append("../..")
import pytest
import numpy as np
from numpy.testing import *


class TestOps(object):
    def test_normalized_cosine(self):
        from scipy.spatial.distance import cdist
        from pyasv.basic.ops import cosine
        import tensorflow as tf
        for i in range(5):
            x = np.random.rand(100, 100)
            y = np.random.rand(1, 100)
            x = x / np.sqrt(np.sum(x ** 2, axis=-1, keepdims=True) + 1e-12)
            y = y / np.sqrt(np.sum(y ** 2, axis=-1, keepdims=True) + 1e-12)
            sess = tf.Session()
            res = sess.run(cosine(x, y, normalized=True, dis=False))
            assert_array_almost_equal(res, 1 - cdist(x, y, metric='cosine'))

    def test_cosine_similarity(self):
        from scipy.spatial.distance import cdist
        from pyasv.basic.ops import cosine
        import tensorflow as tf
        for i in range(5):
            x = np.random.rand(100, 100)
            y = np.random.rand(1, 100)
            sess = tf.Session()
            res = sess.run(cosine(x, y, normalized=False, dis=True))
            assert_array_almost_equal(res, cdist(x, y, metric='cosine'))
