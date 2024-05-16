import json
import math
import gurobipy as gp
import folium
import webbrowser
from gurobipy import GRB
from itertools import combinations

cities_json = json.load(open('Data/20_cities_GER.json'))

coordinates = {}
for city in cities_json:
    coordinates[city['city']] = (float(city['lat']), float(city['lng']))
city_names = list(coordinates.keys())

def get_euclidean_distance(city1, city2):
    return math.sqrt((coordinates[city2][0] - coordinates[city1][0])**2 + (coordinates[city2][1] - coordinates[city1][1])**2)

dist = {(c1, c2): get_euclidean_distance(c1, c2) for c1, c2 in combinations(city_names, 2)}

m = gp.Model()

vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='x')

vars.update({(j,i):vars[i,j] for i,j in vars.keys()})

m.addConstrs(vars.sum(c, '*') == 2 for c in city_names)

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                                if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(city_names):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                            <= len(tour)-1)

def subtour(edges):
    unvisited = city_names[:]
    cycle = city_names[:] 
    while unvisited:  
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(thiscycle) <= len(cycle):
            cycle = thiscycle
    return cycle

m._vars = vars
m.Params.lazyConstraints = 1
m.optimize(subtourelim)

vals = m.getAttr('x', vars)
selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

tour = subtour(selected)
assert len(tour) == len(city_names)

map = folium.Map(location=[51,10], zoom_start = 7)

points = []
for city in tour:
  points.append(coordinates[city])
points.append(points[0])

folium.PolyLine(points).add_to(map)

map.save("tsp_map.html")

webbrowser.open("tsp_map.html")

m.dispose()
gp.disposeDefaultEnv()