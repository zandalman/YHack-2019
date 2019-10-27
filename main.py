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
            break

    URL = res[i]
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')

    places = []
    for place in soup.find_all('span', attrs={'class', 'social-shelf-items-ShelfLocationSection__name--CdA_A'}):
        places.append(place.text)

    return places

def rate(location):
    try:
        gs = Gsearch_python("Tripadvisor %s" % location)
        res = gs.Gsearch()

        for i in range(len(res)):
            if re.search("https://www.tripadvisor.com/Attraction_Review", res[i]) != None:
                break

        URL = res[i]
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html5lib')

        rating = float(str(soup.find_all('div', attrs={'class', 'prw_rup prw_common_bubble_rating rating'})[0]).split("alt=\"")[1].split(" ")[0])
        reviews = int(soup.find_all('span', attrs={'class', 'reviewCount'})[0].text.split("Review")[0][:-1].replace(',',''))
        return [rating, reviews]
    except IndexError:
        return [3, 1]


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

        [rating, reviews] = rate(place)
        return lat, long, rating, reviews, kind

def place_data(place, max_size = 9, offline = True):
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


def google(n, locations):
    gmaps = googlemaps.Client(key=KEY)
    now=datetime.now()

    gmaps_matrix = gmaps.distance_matrix(locations, locations,
                        mode="walking",
                        avoid="ferries",
                        departure_time=now)

    matrix = np.ndarray(dtype="double", shape=(n,n))
    for i in range(n):
        for j in range(n):
            matrix[i][j] = gmaps_matrix['rows'][i]['elements'][j]['duration']['value']

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

def value(path, ratings, reviews):
    n = len(path)
    sum = 0
    for i in range(n):
        if(path[i]!=len(ratings)):
            sum+=float(ratings[path[i]])-(1/(float(reviews[path[i]]))**0.5)
    return sum/n**(0.5)

def best(good, ratings, reviews):
    values = []
    for i in range(len(good)):
        values.append(value(good[i], ratings, reviews))

    max = 0
    loc = -1

    for i in range(len(good)):
        if(values[i]>max):
            max = values[i]
            loc = i

    return good[loc]

def get_path(n, locations, ratings, reviews, names, kinds, sp, time_limit):
    locations = np.append(locations, sp)
    n+=1

    matrix = google(n, locations)
    good = find_route(n, matrix, locations, time_limit)
    best_route = best(good, ratings, reviews)


    print(best_route)
    print(value(best_route, ratings, reviews))

    for i in range(len(best_route)):
        if(best_route[i]!=n-1):
            loc = best_route[i]
            print(names[loc]+ "\t" + locations[loc] + "\t" + ratings[loc] + "\t" + kinds[loc])

    return best_route

def main(city, time_limit):
    data = place_data(city, offline=False)
    names = list(data.keys())
    ratings = list(np.array(list(data.values()))[:, 2])
    reviews = list(np.array(list(data.values()))[:, 3])
    lats = np.array(list(data.values()), dtype=str)[:, 0]
    longs = np.array(list(data.values()), dtype=str)[:, 1]
    comma = np.full(lats.shape, ',')
    locations = list(np.core.defchararray.add(np.core.defchararray.add(lats, comma), longs))
    kinds = list(np.array(list(data.values()))[:, 4])

    gmaps = googlemaps.Client(key=KEY)

    n = len(locations)
    sp = get_sp(city)

    route = get_path(n, locations, ratings, reviews, names, kinds, sp, time_limit)

city = "Chicago"
time_limit = 6000
main(city, time_limit)
