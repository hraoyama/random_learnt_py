import tensorflow.compat.v1 as tf
import tensorflow_probability as tfp
import functools
import operator
import math

tf.disable_v2_behavior()

import numpy as np

def generate_corrMatrix_from_covMatrix(cov_matrix):
    assert cov_matrix.shape[0] == cov_matrix.shape[1]
    d_matrix = np.diag(np.sqrt(np.diag(cov_matrix)))
    d_matrix_inv = np.diag(1.0 / np.diag(d_matrix))
    corr_matrix = np.matmul(np.matmul(d_matrix_inv, cov_matrix), d_matrix_inv)
    return corr_matrix


def generate_series_from_corrMatrix(corr_matrix, num_of_obs):
    assert corr_matrix.shape[0] == corr_matrix.shape[1]
    chol_from_corr = np.linalg.cholesky(corr_matrix)
    random_numbers = np.random.randn(num_of_obs * corr_matrix.shape[0])
    correlated_observations = [
        np.matmul(chol_from_corr,
                  random_numbers[x:x + corr_matrix.shape[0]].reshape(corr_matrix.shape[0], 1))
            .reshape(1, corr_matrix.shape[0])
        for x in range(0, num_of_obs * corr_matrix.shape[0], corr_matrix.shape[0])]
    correlated_observations = np.squeeze(np.stack(correlated_observations))
    return correlated_observations

# Series By Series comparison for covariance matrices
num_of_series = 5
input_shape = [5, num_of_series, num_of_series]
x1 = tf.placeholder(tf.float64, shape=input_shape)
x2 = tf.placeholder(tf.float64, shape=input_shape)
cov[i, j] is the sample covariance between x[:, i, j] and y[:, i, j].
cov = tfp.stats.covariance(x1, x2, sample_axis=0, event_axis=None)
cov_matrix[i, m, n] is the sample covariance of x[:, i, m] and y[:, i, n]
cov_matrix = tfp.stats.covariance(x1, x2, sample_axis=0, event_axis=-1)
with tf.Session() as session:
    a1 = np.random.normal(size=functools.reduce(operator.mul, x1.get_shape()).value).reshape(input_shape)
    a2 = np.random.normal(size=functools.reduce(operator.mul, x2.get_shape()).value).reshape(input_shape)
    result = session.run(cov, feed_dict={x1: a1, x2: a2})
    result2 = session.run(cov_matrix, feed_dict={x1: a1, x2: a2})

check
math.isclose(result[0, 0], np.cov(a1[:, 0, 0], a2[:, 0, 0], bias=True)[0][1], rel_tol=1e-7)

# Fictional correlated time series with 100 observations
num_of_obs = 100
x = tf.random_normal(shape=(num_of_obs, num_of_series))
cov_matrix = tfp.stats.covariance(x, x, sample_axis=0, event_axis=-1)
xvars = tf.math.reduce_variance(x, 0)
with tf.Session() as session:
    (covMatrix, xVars, xInput) = session.run([cov_matrix, xvars, x])

# check
all(map(lambda x: math.isclose(x[0], x[1], rel_tol=1e-5), zip(np.diag(covMatrix), xVars)))

# generate a correlation  matrix from the covariance matrix
np.random.seed(20)
corrMatrix = generate_corrMatrix_from_covMatrix(covMatrix)
generate an example series from the correlation matrix
correlatedObservations = generate_series_from_corrMatrix(corrMatrix, num_of_obs)

# assume a correlation matrix of risk factors/drivers:
driveCorrMatrix = np.array([[1.0, 0.5, -0.2], [0.5, 1.0, 0.1], [-0.2, 0.1, 1.0]])

# assume a population of weights for different scenarios:
np.random.seed(20)
num_of_weights = 1000 * driveCorrMatrix.shape[0]
random_weights = np.reshape(np.random.randn(num_of_weights),
                            (int(num_of_weights / driveCorrMatrix.shape[0]), driveCorrMatrix.shape[0]))
random_weights_normalized = np.apply_along_axis(lambda x: np.divide(x, np.sqrt(np.sum(np.square(x)))), 1,
                                                random_weights)
# generate some scenarios
factor_corr = tf.placeholder(tf.float64)
factor_betas = tf.placeholder(tf.float64)
num_of_simulations = 100

with tf.Session() as session:

# generate some stress scenarios:

correlatedObservations = generate_series_from_corrMatrix(corrMatrix, num_of_obs)









