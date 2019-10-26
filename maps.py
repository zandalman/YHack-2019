import googlemaps
from datetime import datetime

import math
import numpy as np

import mlrose

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
place3 = "43.123, -110.1245"
places = [place1, place2, place3]
n = len(places)

gmaps_matrix = gmaps.distance_matrix(places, places,
                    mode="driving",
                    avoid="ferries",
                    departure_time=now)

matrix = np.ndarray(dtype="double", shape=(n,n))
for i in range(n):
    for j in range(n):
        matrix[i][j] = gmaps_matrix['rows'][i]['elements'][j]['duration_in_traffic']['value']

def getMat(iArr):
    n = len(iArr)
    new_mat = np.ndarray(dtype="double", shape=(n,n))
    for i in range(n):
        for j in range(n):
            new_mat[i][j] = matrix[iArr[i]][iArr[j]]

    return new_mat

def binary(n, digits):
    binary = str("{0:b}".format(n))
    return (digits-len(binary))*"0"+binary

for i in range(1, 2**n):
    bin = binary(i, n)
    iArr = []
    posArr = []
    for j in range(n):
        if(bin[j]=='1'):
            iArr.append(j)
            posArr.append(places[j])

    if(len(iArr)>1):
        new_mat = getMat(iArr)
        print(iArr)
        print(new_mat)
        print()
