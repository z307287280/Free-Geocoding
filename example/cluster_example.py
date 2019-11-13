from cluster import Optimization
import pandas as pd

if __name__ == '__main__':
    data = pd.read_csv('coordinate_batch_1.csv')
    x = Optimization.elbowMethod(data, col=['Latitude', 'Longitude'], plot=True)
    center = Optimization.optimal_center(data, col=['Latitude', 'Longitude'], miles=30)
    print(center)