import requests
import re
from bs4 import BeautifulSoup
from google_images_download import google_images_download   #importing the library
from IPython.display import Image
import googlemaps
from datetime import datetime
import numpy as np
import json
import geocoder
import mlrose
import matplotlib.pyplot as plt


KEY_file = open('key.txt', 'r')
KEY=KEY_file.readlines()[0]

class Gsearch_python:

    def __init__(self, name_search):
        self.name = name_search

    def Gsearch(self):
        count = 0
        results = []

        try:
            from googlesearch import search
        except ImportError:
             print("No Module named 'google' Found")

        for i in search(query=self.name,tld='co.in',lang='en',num=10,stop=10,pause=2):
            results.append(i)

        return results

def places(city):
    gs = Gsearch_python("Tripadvisor %s" % (city))
    res = gs.Gsearch()

    for i in range(len(res)):
        if re.search("https://www.tripadvisor.com/Tourism", res[i]) != None:
            trip = i
            break

    URL = res[i]
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')

    places = []
    for place in soup.find_all('span', attrs={'class', 'social-shelf-items-ShelfLocationSection__name--CdA_A'}):
        places.append(place.text)

    return places

def info(place):
    gmaps = googlemaps.Client(key=KEY)
    geocode_result = gmaps.geocode(place)
    place_id = geocode_result[0]['place_id']

    URL2 = 'https://maps.googleapis.com/maps/api/place/details/json?place_id=%s&fields=name,rating,photos,type&key=%s'% (place_id, KEY)
    r2 = requests.get(URL2)
    soup2 = BeautifulSoup(r2.content, 'html5lib')
    res2 = json.loads(r2.text)

    good_types = ['amusement_park', 'aquarium', 'art_gallery', 'bakery',
        'book_store', 'bowling_alley', 'campground',
        'casino', 'cemetery', 'church', 'city_hall', 'courthouse',
        'embassy', 'hindu_temple', 'jewelry_store', 'library',
        'mosque', 'museum', 'park', 'stadium', 'synagogue', 'tourist_attraction', 'zoo']

    if not set(res2['result']['types']).isdisjoint(good_types):
        lat = geocode_result[0]['geometry']['location']['lat']
        long = geocode_result[0]['geometry']['location']['lng']
        kind = res2['result']['types'][0]

        try: rating = float('%.4g' % str(res2['result']['rating']))
        except: rating = 4.5

        return lat, long, rating, kind

def place_data(place, max_size = 5, offline = True):
    if offline == True:
        mem = np.load('memory.npz')
        try: return mem[place].item()
        except: data = None
    else:
        loc = places(place)
        data = {}

        count = 0
        for i in range(len(loc)):
            if(count==max_size): break
            place_info = info(place + loc[i])
            if (place_info != None) and (place_info not in data.values()):
                data[loc[i]] = place_info
                count+=1

        mem = {place: data}
        np.savez('memory.npz', **mem)

        return data

data = place_data('New York', offline=False)
names = list(data.keys())
ratings = list(np.array(list(data.values()))[:, 2])
lats = np.array(list(data.values()), dtype=str)[:, 0]
longs = np.array(list(data.values()), dtype=str)[:, 1]
comma = np.full(lats.shape, ',')
locations = list(np.core.defchararray.add(np.core.defchararray.add(lats, comma), longs))
kinds = list(np.array(list(data.values()))[:, 3])

def get_sp(place):
    if place == 'current':
        g = geocoder.ip('me')
        sp = str(g.latlng[0]) + ',' + str(g.latlng[1])
    else:
        gmaps = googlemaps.Client(key=KEY)
        geocode_result = gmaps.geocode(place)
        lat = geocode_result[0]['geometry']['location']['lat']
        long = geocode_result[0]['geometry']['location']['lng']
        sp = str(lat) + ',' + str(long)

    return sp

#res2 = json.loads(r2.text)
#photo_ref = res2['result']['photos'][0]['photo_reference']

#URL3 = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=%s&key=AIzaSyCp1XU9QMczMh_iDm8hEKrWjYu4ZY2ki5k' % photo_ref
#r3 = requests.get(URL3)

def pic(place):
    response = google_images_download.googleimagesdownload()   #class instantiation
    arguments = {"keywords":"%s %s" % (city, place),"limit":1,"print_urls":True}
    paths = response.download(arguments)
    img = Image(filename=paths[0][city + ' ' + place][0])
    return img

now=datetime.now()
gmaps = googlemaps.Client(key=KEY)

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

def find_route(n, matrix, locations, time_limit):
    good = []
    for i in range(1, 2**(n-1)):
        bin = binary(i, n-1)+"1"
        iArr = []
        posArr = []
        for j in range(n):
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

    return good[loc]

n = len(locations)

time_limit = 7200
sp = get_sp('New York')

def get_path(n, locations, ratings, names, kinds, sp, time_limit):
    locations = np.append(locations, sp)
    n+=1

    matrix = google(n, locations)
    good = find_route(n, matrix, locations, time_limit)
    best_route = best(good, ratings)


    print(best_route)
    print(value(best_route, ratings))

    for i in range(len(best_route)):
        if(best_route[i]!=n-1):
            loc = best_route[i]
            print(names[loc]+ "\t" + locations[loc] + "\t" + ratings[loc] + "\t" + kinds[loc])

    return best_route

print(n)
route = get_path(n, locations, ratings, names, kinds, sp, time_limit)

data_small = {}

for i in range(5):
    data_small[list(data.keys())[i]] = list(data.values())[i]

names = list(data_small.keys())
ratings = np.array(list(data_small.values()))[:, 2]
lats = np.array(list(data_small.values()), dtype=str)[:, 0]
longs = np.array(list(data_small.values()), dtype=str)[:, 1]
comma = np.full(lats.shape, ',')
locations = np.core.defchararray.add(np.core.defchararray.add(lats, comma), longs)
kinds = np.array(list(data_small.values()))[:, 3]
