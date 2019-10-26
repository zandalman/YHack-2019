import requests
import re
from bs4 import BeautifulSoup
from google_images_download import google_images_download   #importing the library
from IPython.display import Image
import googlemaps
from datetime import datetime
import numpy as np

#Get API key
KEY_file = open('key.txt', 'r')
KEY=KEY_file.readlines()[0]

#List types of places that are interesting
good_types = ['amusement_park', 'aquarium', 'art_gallery', 'bakery', 'bar',
    'bicycle_store', 'book_store', 'bowling_alley', 'cafe', 'campground',
    'casino', 'cemetery', 'church', 'city_hall', 'courthouse',
    'embassy', 'florist', 'hindu_temple', 'jewelry_store', 'library', 'light_rail_station',
    'mosque', 'movie_theater', 'museum', 'night_club', 'park', 'restaurant',
    'spa', 'stadium', 'synagogue', 'tourist_attraction', 'zoo']

#Define a Google search object
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

#Get a list of places in a city from TripAdvisor
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

#Return latitude, longitude, and rating for a given location
def info(place):

    gmaps = googlemaps.Client(key=KEY)

    geocode_result = gmaps.geocode(place)
    place_id = geocode_result[0]['place_id']

    URL2 = 'https://maps.googleapis.com/maps/api/place/details/json?place_id=%s&fields=name,rating,photos,type&key=%s'% (place_id, KEY)
    r2 = requests.get(URL2)
    soup2 = BeautifulSoup(r.content, 'html5lib')
    res2 = json.loads(r2.text)

    if not set(res2['result']['types']).isdisjoint(good_types):

        lat = geocode_result[0]['geometry']['location']['lat']
        long = geocode_result[0]['geometry']['location']['lng']
        try:
            rating = float('%.3g' % str(res2['result']['rating']))
        except:
            rating = 4.5

        return lat, long, rating

#Return a dictionary of interesting locations in a place with latitude, longitude, and rating
def place_data(place):

    loc = places(place)

    data = {}

    for i in range(len(loc)):

        place_info = info(place + loc[i])

        if (place_info != None) and (place_info not in data.values()):

            data[loc[i]] = place_info

    return data
