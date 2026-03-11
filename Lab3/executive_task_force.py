import gurobipy as gp
from gurobipy import GRB

model = gp.Model("Team_Politics")

# Variables: 8 Executives
execs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
x = model.addVars(execs, vtype=GRB.BINARY, name="Select")

# z = 1 if A and B are BOTH selected
z = model.addVar(vtype=GRB.BINARY, name="Alliance_AB")

# Constraints

# Total team size must be 4
model.addConstr(gp.quicksum(x[i] for i in execs) == 4, "Team_Size")

# IF (A and B are selected) THEN z = 1
# This is a standard linearization of z = xA * xB
model.addConstr(z >= x['A'] + x['B'] - 1, "Trigger_If")

# IF z = 1 THEN (C and D cannot both be selected)
# xC + xD <= 1 if z=1, else <= 2
model.addConstr(x['C'] + x['D'] <= 2 - z, "Enforce_Then")

# Objective: Maximize total "Experience Points" 
# (Let's give each exec a score)
scores = {'A': 10, 'B': 9, 'C': 8, 'D': 8, 'E': 5, 'F': 5, 'G': 4, 'H': 4}
model.setObjective(gp.quicksum(scores[i] * x[i] for i in execs), GRB.MAXIMIZE)

model.optimize()

if model.status == GRB.OPTIMAL:
    selected = [i for i in execs if x[i].x > 0.5]
    print(f"Final Task Force: {selected}")
    print(f"Alliance A-B Active: {'Yes' if z.x > 0.5 else 'No'}")
    print(f"Total Experience: {model.objVal}")