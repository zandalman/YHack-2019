import googlemaps
from datetime import datetime

import math
import numpy as np

import mlrose

f = open("key.txt","r")
key = f.readlines()[0]
gmaps = googlemaps.Client(key=key)

def google(n, locations):
    gmaps_matrix = gmaps.distance_matrix(locations, locations,
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
        for j in range(n - 1):
            if(bin[j]=='1'):
                iArr.append(j)
                posArr.append(locations[j])

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
            sum+=float(ratings[path[i]])
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

n = len(locations)

time_limit = 3600

def get_path(n, locations, ratings, names, kinds, sp, time_limit):
    locations = np.append(locations, sp)
    n+=1

    matrix = google(n, locations)
    good = find_route(n, matrix, time_limit)
    best_route = best(good, ratings)

    print(best_route)
    print(value(best_route, ratings))

get_path(n, locations, ratings, names, kinds, sp, time_limit)

"""
changed places to locations
changed types to kinds
changed start_pos to sp
changed n to n-1 in find_route()
added float() around ratings[path[i]] in best()
"""
