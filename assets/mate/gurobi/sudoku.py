import gurobipy as gp
from gurobipy import GRB

sudoku = """5 3 . . 7 . . . .
6 . . 1 9 5 . . .
. 9 8 . . . . 6 .
8 . . . 6 . . . 3
4 . . 8 . 3 . . 1
7 . . . 2 . . . 6
. 6 . . . . 2 8 .
. . . 4 1 9 . . 5
. . . . 8 . . 7 9"""

grid = [row.strip().split(' ') for row in sudoku.split("\n")]

n = 9 # size of the grid

model = gp.Model('sudoku')
vars = model.addVars(n, n, n, vtype=GRB.BINARY, name='G')

# Fix variables associated with cells whose values are pre-specified
for i in range(n):
    for j in range(n):
        if grid[i][j] != '.':
            k = int(grid[i][j]) - 1
            vars[i, j, k].LB = 1

# Each cell must take one value
model.addConstrs(
    (vars.sum(i, j, '*') == 1
    for i in range(n)
    for j in range(n)), name='V');

# Each value appears once per row
model.addConstrs(
    (vars.sum(i, '*', k) == 1
    for i in range(n)
    for k in range(n)), name='R');

# Each value appears once per column
model.addConstrs(
    (vars.sum('*', j, k) == 1
    for j in range(n)
    for k in range(n)), name='C');

# Each value appears once per subgrid
s = 3 # sub-grid size
model.addConstrs((
    gp.quicksum(vars[i, j, k] for i in range(i0*s, (i0+1)*s)
                for j in range(j0*s, (j0+1)*s)) == 1
    for k in range(n)
    for i0 in range(s)
    for j0 in range(s)), name='Sub');

# Solve and print
model.optimize() # No objective!!

solution = model.getAttr('X', vars)
sol = ''
for i in range(n):
    for j in range(n):
        for v in range(n):
            if solution[i, j, v] > 0.5:
                sol += str(v+1) + ' '
    sol += '\n'
print(sol)