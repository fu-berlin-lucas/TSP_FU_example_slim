import gurobipy as gp
from gurobipy import GRB
from itertools import combinations

def solve_tsp(dist, city_names):
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
    m.dispose()
    gp.disposeDefaultEnv()
    return tour