import sys
sys.path.append("..")
import numpy as np
from pyasv.basic.layers import attention_pooling
import tensorflow as tf

x = tf.ones(dtype=tf.float32, shape=[2, 3, 4, 5])

y = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float32)

y = [y, y, y]
y = [y, y]
y = np.array(y, dtype=np.float32)
y = tf.constant(y)

y = tf.reshape(y, shape=[2, 3, 5, 1])

sess = tf.Session()

print(sess.run(tf.matmul(x ,y)))
