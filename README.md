# Free-Geocoding
This is a small packge of geocoding(basically is a small project when I was at University), it helps to transform physical address into coordinates automatically. The package also offers the clustering method, the users can apply it to find the central location of a cluster.

# transformer.py
This file provides multiprocessing for geocoding, meanwhile, I only found two possibile free-geocoders, the maximum multiprocessesor will be 2. However, the user can add their own encoders that links to geopy package to the '__encoder__' variable. In order to face the situation of transformation disruptted, it is able to record current transformed data in log and store them in minibatches, users can assign the output directory for those minibatches. When the transformation has been disruptted, uses can restart it again from the last check point.

# cluster.py
This file provides clustering function to find the optimal centers of each cluster, the algorithm is based on K-means and Elbow method. It allows the user to choose optimal k automatically. However, in some situation, Elbow method doesn't work very well. Users need to apply plot function in the file to judge if it is necessary to use K-means.
