import time
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from geopy import distance
import matplotlib.pyplot as plt
from kneed import KneeLocator


class Optimization:
    def elbowPlot(K, distortions):
        plt.plot(K, distortions, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Distortion')
        plt.title('The Elbow Method showing the optimal k')
        plt.show()

    def elbowMethod(data, col, n_opt='opt', k=10, plot=False, verbose=True):
        if not isinstance(n_opt, (str, int)):
            raise TypeError('n_opt needs to be str or int')
        if n_opt is int and n_opt > k:
            raise ValueError('n_opt cannot be greater than k, either input a lower k or lower n_opt')

        s = time.time()
        distortions, labels, centriods = [], [], []
        res = defaultdict(list)
        K = range(1, k + 1)
        X = data[col]
        for k in K:
            kmeanModel = KMeans(n_clusters=k)
            kmeanModel.fit(X)
            distortion = sum(np.min(cdist(X, kmeanModel.cluster_centers_, 'euclidean'), axis=1)) / X.shape[0]
            distortions.append(distortion)
            labels.append(kmeanModel.labels_)
            centriods.append(kmeanModel.cluster_centers_)

        if plot:
            Optimization.elbowPlot(K, distortions)
        if n_opt == 'opt':
            optimal = KneeLocator(K, distortions, curve='convex', direction='decreasing').knee
            clusters = labels[optimal - 1]
        else:
            clusters = labels[n_opt - 1]
        for x, y in zip(data[col].values, clusters):
            res[y].append((x[0], x[1]))
        e = time.time() - s
        if verbose:
            print('Data Size:%d  Optimal_K:%d  Process Time:%d seconds' % (len(data), len(res), e))
        return res

    def optimization(res, miles, k=5, verbose=True):
        s = time.time()
        result = []
        centroids = []
        for i in range(len(res)):
            kmeans = KMeans(1)
            kmeans.fit(res[i])
            centroids.append(tuple(kmeans.cluster_centers_))

        for j in range(len(res)):
            lst = [(0, centroids[j])]
            for coordinate in res[j]:
                dis = distance.distance(centroids[j], coordinate).miles
                lst.append((dis, coordinate))
            result.append(sorted(lst, key=lambda x: x[0])[:k])

        center = []
        for k in range(len(result)):
            temp = (0, 0)
            for candidate in result[k]:
                count = 0
                for coordinate in res[k]:
                    dis = distance.distance(candidate[1], coordinate).miles
                    if dis <= miles:
                        count += 1
                temp = max(temp, (candidate[1], count), key=lambda x: x[1])
            center.append(temp)
        e = time.time() - s
        if verbose:
            print('Process Time: %.1f mins' % (e / 60))
        return center

    def optimal_center(data, col, miles, n_opt='opt', n_rounds=5, elb_k=10):
        s = time.time()
        res = Optimization.elbowMethod(data, col, n_opt=n_opt, k=elb_k, verbose=False)
        center = Optimization.optimization(res, miles, k=n_rounds, verbose=False)
        e = time.time() - s
        print('Area Coverage: %.2f' % (sum([x[1] for x in center]) / len(data)), end='  ')
        print('Process Time: %.1f mins' % (e / 60))
        return center