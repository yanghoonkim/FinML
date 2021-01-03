''' Essential packages '''
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt

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

        self.weight = -lambda1 * self.covariance_inverse @ self.mean_return - \
        lambda2 * self.covariance_inverse @ self.ones_vector


    def portfolio_statistics(self):
        mean_p = 0
        for m, w in zip(self.mean_return, self.weight):
            mean_p += m[0]*w[0]

        cov_p = np.matmul(np.matmul(self.weight.T, self.covariance), self.weight)
        return mean_p, cov_p[0][0]

    def plot(self, show=True, save_path=None):
        x, y = [], []

        mean_max, mean_min = max(self.mean_return), min(self.mean_return)
        divide = 100
        for idx in range(divide + 1):
            mean_target = mean_min + (float(idx) / float(divide)) * (mean_max - mean_min)
            self.get_weight(mean_target)
            mean_portfolio, covariance_portfolio = self.portfolio_statistics()

            x.append(covariance_portfolio)
            y.append(mean_portfolio)

        plt.plot(x, y, color='black')
        plt.xlabel('std')
        plt.ylabel('mean')

        if save_path:
            if save_path.split('.')[-1].lower() in ['png', 'jpg', 'jpeg', 'bmp']:
                plt.savefig(save_path)
            else:
                plt.savefig(os.path.join(save_path, str(datetime.now())[:10] + '_simple_mean_variance.jpg'))

        if show:
            plt.show()
