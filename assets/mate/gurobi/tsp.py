import math
import random
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
from matplotlib import collections  as mc

# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, status):
    if status == GRB.Callback.MIPSOL:
        n = model._ncities
        vals = model.cbGetSolution(model._vars)
        tour = subtour(vals, n) # Shortest cycle
        if len(tour) < n:
            model.cbLazy(
                gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2)) <= len(tour)-1
            )

# Given a tuplelist of edges, find the shortest subtour
def subtour(vals, n):
    # Active edges
    edges = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)
    unvisited = list(range(n))
    cycle = range(n+1)  # Initial length has 1 more city
    while unvisited:  # True while list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle


def plottour(m, points):
    vals = m.getAttr('X', vars)
    edges = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)
    fig, ax = plt.subplots()

    # Add the path
    lines = [[points[i], points[j]] for i,j in edges]
    lc = mc.LineCollection(lines, linewidths=1)
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    
    # Highlight the points
    ax.scatter([p[0] for p in points], [p[1] for p in points], marker='H', c='r')
    for i, p in enumerate(points):
        ax.annotate(str(i), (p[0], p[1]))
    ax.plot()
    plt.show()



random.seed(42)

# Number of points
n = 50
points = [(random.randint(0, 100), random.randint(0, 100)) for i in range(n)]

# Adjacency matrix
dist = {(i, j):
        math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2)))
        for i in range(n) for j in range(i)}

m = gp.Model()

# Variables
vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')

# Simmetry constraints
for i, j in vars.keys():
    vars[j, i] = vars[i, j]

# Degree-2 constraints
m.addConstrs(vars.sum(i, '*') == 2 for i in range(n))

m._ncities = n
m._vars = vars
m.Params.LazyConstraints = 1
m.optimize(subtourelim)

vals = m.getAttr('X', vars)
tour = subtour(vals, n)
assert len(tour) == n

plottour(m, points)

print('Optimal tour: %s' % str(tour))
print('Optimal cost: %g' % m.ObjVal)
