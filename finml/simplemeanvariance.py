''' Meta Data '''
__title__ = 'mean variance portfolio optimization'
__version__ = '1.0.0'
__author__ = 'Kiyoung Kim (kky416@snu.ac.kr)'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020 by Kiyoung Kim'

''' Essential packages '''
import numpy as np

class SimpleMeanVariance:
    def __init__(self, mean_return, covariance):
        self.mean_return = mean_return
        self.covariance = covariance
        self.covariance_inverse = np.linalg.inv(self.covariance)

        self.ones_vector = np.ones((len(self.mean_return), 1))

    def get_weight(self, target_return):

        # @ == np.matmul
        lambda2 = (target_return * self.ones_vector.T @ self.covariance_inverse @ self.mean_return - \
              self.mean_return.T @ self.covariance_inverse @ self.mean_return) / \
        ((self.ones_vector.T @ self.covariance_inverse @ self.ones_vector) * \
         (self.mean_return.T @ self.covariance_inverse @ self.mean_return) - \
        (self.ones_vector.T @ self.covariance_inverse @ self.mean_return) * \
         (self.mean_return.T @ self.covariance_inverse @ self.ones_vector))
        
        lambda1 = -(lambda2 * self.mean_return.T @ self.covariance_inverse @ self.ones_vector + target_return) / \
                  (self.mean_return.T @ self.covariance_inverse @ self.mean_return)

        weight = -lambda1 * self.covariance_inverse @ self.mean_return - \
        lambda2 * self.covariance_inverse @ self.ones_vector

        return weight

    def portfolio_statistics(self, weight):
        mean_p = 0
        for m, w in zip(self.mean_return, weight):
            mean_p += m[0]*w[0]

        cov_p = np.matmul(np.matmul(weight.T, self.covariance), weight)
        return mean_p, cov_p[0][0]