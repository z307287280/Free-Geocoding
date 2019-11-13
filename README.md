# Free-Geocoding
This is a small packge of geocoding, it helps to transform physical address into coordinates automatically. The package also offers the clustering method, the user can apply it to find the central location of a cluster.

# transformer.py
This file provides multiprocessing for geocoding, meanwhile, I only found two possibile free-geocoders, the maximum multiprocessesor will be 2. However, the user can add their own encoders that links to geopy package to the '__encoder__' variable. 

# cluster.py
This file provides clustering function to find the optimal centers of each cluster, the algorithm is based on K-means and Elbow method. It allows the user to choose optimal k automatically. However, in some situation, Elbow method doesn't work very well. Users can apply plot function in the file to judge if it is necessary to use elbow method.
