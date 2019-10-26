import googlemaps
from datetime import datetime

import numpy as np

f = open("key.txt","r")
key = f.readlines()[0]
gmaps = googlemaps.Client(key=key)

now=datetime.now()
directions_result = gmaps.directions("37.2753,-107.880067",
                                     "37.7749,-122.419416",
                                     mode="driving",
                                     avoid="ferries",
                                     departure_time=now)

print(directions_result[0]['legs'][0]['distance']['text'])
print(directions_result[0]['legs'][0]['duration']['text'])

place1 = "37.2753,-107.88067"
place2 = "37.7749,-122.419416"
places = [place1, place2]
n = len(places)

gmaps_matrix = gmaps.distance_matrix(places, places,
                    mode="driving",
                    avoid="ferries",
                    departure_time=now)

print(gmaps_matrix['rows'][1]['elements'])


matrix = np.ndarray(dtype="double", shape=(n,n))
for i in range(n):
    for j in range(n):
        matrix[i][j] = gmaps_matrix['rows'][i]['elements'][j]['duration_in_traffic']['value']

print(matrix)
