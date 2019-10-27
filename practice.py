
import gmaps
import matplotlib.pyplot as plt

#configure api
gmaps.configure(api_key="AIzaSyDQnwTnorktn6rmb0FDyaV_M8IgeVWklaY")
#Define location 1 and 2
Durango = (37.2753,-107.880067)
SF = (37.7749,-122.419416)
#Create the map
fig = gmaps.figure()
#create the layer
layer = gmaps.directions.Directions(Durango, SF,mode='car')
#Add the layer
fig.add_layer(layer)
fig

'''
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key="AIzaSyDQnwTnorktn6rmb0FDyaV_M8IgeVWklaY")


now = datetime.now()
directions_result = gmaps.directions("37,-107", "37,-122", mode = "driving", departure_time=now)


print(directions_result[0]['legs'][0]['distance']['text'])
print(directions_result[0]['legs'][0]['duration']['text'])
'''
