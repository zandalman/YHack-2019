import requests
import re
from bs4 import BeautifulSoup
from google_images_download import google_images_download   #importing the library
import googlemaps

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

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(r.content, 'html5lib')

    places = []

    for place in soup.find_all('span', attrs={'class', 'social-shelf-items-ShelfLocationSection__name--CdA_A'}):
        places.append(place.text)

    return places

def pic(city, place):

    response = google_images_download.googleimagesdownload()   #class instantiation

    arguments = {"keywords":"%s %s" % (city, place),"limit":1,"print_urls":True}   #creating list of arguments
    paths = response.download(arguments)   #passing the arguments to the function
    Image(filename=paths[0][city + ' ' + place][0])    #printing absolute paths of the downloaded images

def info(place):

    gmaps = googlemaps.Client(key='AIzaSyCp1XU9QMczMh_iDm8hEKrWjYu4ZY2ki5k')

    geocode_result = gmaps.geocode(place)
    place_id = geocode_result[0]['place_id']

    URL2 = 'https://maps.googleapis.com/maps/api/place/details/json?place_id=%s&fields=name,rating,photos,url&key=AIzaSyCp1XU9QMczMh_iDm8hEKrWjYu4ZY2ki5k'% place_id
    r2 = requests.get(URL2)
    soup2 = BeautifulSoup(r.content, 'html5lib')
    res2 = json.loads(r2.text)

    lat = geocode_result[0]['geometry']['location']['lat']
    long = geocode_result[0]['geometry']['location']['lng']
    try:
        rating = res2['result']['rating']
    except:
        rating = 2.5

    return lat, long, rating
