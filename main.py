import json
import math
import folium
import webbrowser
from itertools import combinations
from lib import tsp_solver

cities_json = json.load(open('Data/20_cities_GER.json'))

coordinates = {}
for city in cities_json:
    coordinates[city['city']] = (float(city['lat']), float(city['lng']))
city_names = list(coordinates.keys())

def get_euclidean_distance(city1, city2):
    return math.sqrt((coordinates[city2][0] - coordinates[city1][0])**2 + (coordinates[city2][1] - coordinates[city1][1])**2)

dist = {(c1, c2): get_euclidean_distance(c1, c2) for c1, c2 in combinations(city_names, 2)}

tour = tsp_solver.solve_tsp(dist,city_names)

map = folium.Map(location=[51,10], zoom_start = 7)

points = []
for city in tour:
  points.append(coordinates[city])
points.append(points[0])

folium.PolyLine(points).add_to(map)

map.save("tsp_map.html")

webbrowser.open("tsp_map.html")

