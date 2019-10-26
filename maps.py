import googlemaps
from datetime import datetime

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
