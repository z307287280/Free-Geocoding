# Free-Geocoding
This is a small packge of geocoding, it helps to transform physical address into coordinates automatically. The package also offers the clustering method, the user can apply it to find the central location of a cluster.

# transformer.py
This file provide multiprocessing for geocoding, meanwhile, I only found two possibile free-geocoders, the maximum multiprocessesor will be 2. However, the user can add their own encoders that links to geopy package to the '__encoder__' variable. 

