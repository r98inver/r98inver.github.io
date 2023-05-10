import math
import random
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt


# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, status):
    if status == GRB.Callback.MIPSOL:
        n = model._ncities
        vals = model.cbGetSolution(model._vars)
        tour = subtour(vals, n) # Shortest cycle
        if len(tour) < n:
            m._lazycalls += 1
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

random.seed(42)

# Number of points
call_dic = {}
for n in range(5,100):

    print(f'{n = }')
    call_dic[n] = 0
    n_iter = 10
    for k in range(n_iter):
        points = [(random.randint(0, 100), random.randint(0, 100)) for i in range(n)]

        # Adjacency matrix
        dist = {(i, j):
                math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2)))
                for i in range(n) for j in range(i)}

        # Supress log
        with gp.Env(empty=True) as env:
            # env.setParam("WLSAccessID", str)
            # env.setParam("WLSSECRET", str)
            env.setParam("LICENSEID", 0)
            env.setParam("OutputFlag", 0)
            env.start()

            with gp.Model(env=env) as m:
                vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')
                for i, j in vars.keys():
                    vars[j, i] = vars[i, j]

                m.addConstrs(vars.sum(i, '*') == 2 for i in range(n))

                m._ncities = n
                m._lazycalls = 0
                m._vars = vars
                m.Params.LazyConstraints = 1
                m.optimize(subtourelim)

                vals = m.getAttr('X', vars)
                tour = subtour(vals, n)
                assert len(tour) == n
                call_dic[n] += m._lazycalls
    call_dic[n] /= n_iter

plt.plot(call_dic.keys(), call_dic.values(), label='Constr. calls')
plt.plot(range(5, n), range(5, n), 'r', label='y=x')
plt.legend(loc="upper left")

plt.show()