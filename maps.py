import googlemaps
from datetime import datetime

import math
import numpy as np

import mlrose

f = open("key.txt","r")
key = f.readlines()[0]
gmaps = googlemaps.Client(key=key)

now=datetime.now()

def google(n, places):
    gmaps_matrix = gmaps.distance_matrix(places, places,
                        mode="driving",
                        avoid="ferries",
                        departure_time=now)

    matrix = np.ndarray(dtype="double", shape=(n,n))
    for i in range(n):
        for j in range(n):
            matrix[i][j] = gmaps_matrix['rows'][i]['elements'][j]['duration_in_traffic']['value']

    return matrix

def getMat(iArr, matrix):
    n = len(iArr)
    new_mat = np.ndarray(dtype="double", shape=(n,n))
    for i in range(n):
        for j in range(n):
            new_mat[i][j] = matrix[iArr[i]][iArr[j]]

    return new_mat

def binary(n, digits):
    binary = str("{0:b}".format(n))
    return (digits-len(binary))*"0"+binary

def find_route(n, matrix, time_limit):
    good = []
    for i in range(1, 2**(n-1)):
        bin = binary(i, n-1)+"1"
        iArr = []
        posArr = []
        for j in range(n):
            if(bin[j]=='1'):
                iArr.append(j)
                posArr.append(places[j])

        if(len(iArr)>1):
            new_mat = getMat(iArr, matrix)
            dist_list = []
            for j in range(len(iArr)):
                for k in range(j+1, len(iArr)):
                    dist_list.append((j, k, new_mat[j][k]))

            fitness_dists = mlrose.TravellingSales(distances=dist_list)
            problem_fit = mlrose.TSPOpt(length=len(iArr), fitness_fn=fitness_dists, maximize=False)
            best_state, best_fitness = mlrose.genetic_alg(problem_fit, random_state=2)

            best_state_fr = []
            for k in range(len(iArr)):
                best_state_fr.append(iArr[best_state[k]])

            if(best_fitness<time_limit):
                good.append(best_state_fr)

    return good

def value(path, ratings):
    n = len(path)
    sum = 0
    for i in range(n):
        if(path[i]!=len(ratings)):
            sum+=ratings[path[i]]
    return sum/n**(0.5)

def best(good, ratings):
    values = []
    for i in range(len(good)):
        values.append(value(good[i], ratings))

    max = 0
    loc = -1

    for i in range(len(good)):
        if(values[i]>max):
            max = values[i]
            loc = i

    return good[i]

place0 = "37.2753,-107.88067"
place1 = "37.7749,-122.419416"
place2 = "43.123,-110.1245"
places = [place0, place1, place2]
ratings = [4.5, 3.4, 2.9]

n = len(places)

start_pos = "37,-121"
time_limit = 150000

names = ["Jade", "Phoenix", "Sumedha"]
types = ["Ben", "Zack", "Abhijit"]

def get_path(n, places, ratings, names, types, start_pos, time_limit):
    places.append(start_pos)
    n+=1

    matrix = google(n, places)
    good = find_route(n, matrix, time_limit)
    best_route = best(good, ratings)

    print("Itinerary")
    for i in range(len(best_route)):
        if(best_route[i]!=len(names)):
            print(types[best_route[i]]+"\t"+names[best_route[i]])


get_path(n, places, ratings, names, types, start_pos, time_limit)
