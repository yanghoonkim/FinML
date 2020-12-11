''' Essential packages '''
import numpy as np

class RiskAverseOptimization:
    '''
    Maximize: \mu.T @ wts - \gamma * wts.T @ cov @ wts
    Subject to:  ones.T @ wts = 1, wts >= 0
    '''
    def __init__(self, mean_return, covariance):
        self.mean_return = mean_return
        self.covariance = covariance
        self.covariance_inverse = np.linalg.inv(self.covariance)

        self.ones_vector = np.ones((len(self.mean_return), 1))

    def get_weight(self, gamma):
        coef = (self.ones_vector.T @ self.covariance_inverse @ self.mean_return - gamma) / \
               (self.ones_vector.T @ self.covariance_inverse @ self.ones_vector)
        wts = 1/gamma * self.covariance_inverse @ (self.mean_return - coef * self.ones_vector)
        
        return wts

    def portfolio_statistics(self, wts):
        mean_p = 0
        for m, w in zip(self.mean_return, wts):
            mean_p += m[0]*w[0]

        cov_p = np.matmul(np.matmul(wts.T, self.covariance), wts)
        return mean_p, cov_p[0][0]
