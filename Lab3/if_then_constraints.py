import gurobipy as gp
from gurobipy import GRB

model = gp.Model("If_Then_User_Formulation")

# Variables
x = model.addVar(name="x")
y = model.addVar(name="y")
z = model.addVar(vtype=GRB.BINARY, name="z")

# Parameters
M = 1000
epsilon = 0.0001
b1 = 10
b2 = 5

# Formulation:
# If f(x) <= 10, then g(x) <= 5
# Assuming f(x) = x and g(x) = y for this example:

# 1. Trigger: b1 - f(x) + epsilon <= Mz
model.addConstr(b1 - x + epsilon <= M * z, name="If_Trigger")

# 2. Enforcement: g(x) <= b2 + M(1-z)
model.addConstr(y <= b2 + M * (1 - z), name="Then_Enforce")

model.optimize()