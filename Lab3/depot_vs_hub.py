import gurobipy as gp
from gurobipy import GRB

# Initialize the model
model = gp.Model("Linear_ScaleUp_Dilemma")

# DECISION VARIABLES
# Binary Switch: 1 if Large Hub, 0 if Small Depot
y = model.addVar(vtype=GRB.BINARY, name="is_large_hub")

# Continuous tonnage variables for each specific case
x_small = model.addVar(lb=0, name="tons_in_depot")
x_large = model.addVar(lb=0, name="tons_in_hub")

# LINEAR OBJECTIVE FUNCTION
# Maximize: (Profit_Small * x_small - Fixed_Small_if_y=0) + (Profit_Large * x_large - Fixed_Large_if_y=1)
# Note: Since y=0 means Small, we use (1-y) for the small fixed cost.
profit_small = 3 * x_small - 200 * (1 - y)
profit_large = 5 * x_large - 1500 * y

model.setObjective(profit_small + profit_large, GRB.MAXIMIZE)

# CONSTRAINTS (The Connecting Logic)

# A. Small Depot Bounds: If y=1, x_small is forced to 0. If y=0, max is 100.
model.addConstr(x_small <= 100 * (1 - y), name="Small_Depot_Cap")

# B. Large Hub Bounds: If y=0, x_large is forced to 0. If y=1, range is [500, 2000].
model.addConstr(x_large <= 2000 * y, name="Large_Hub_Max_Cap")
model.addConstr(x_large >= 500 * y, name="Large_Hub_Min_Thresh")

# OPTIMIZE
model.optimize()

# OUTPUT RESULTS
if model.status == GRB.OPTIMAL:
    print("-" * 30)
    if y.x > 0.5:
        print(f"Decision: Build the LARGE HUB")
        print(f"Optimal Tonnage: {x_large.x} tons")
    else:
        print(f"Decision: Build the SMALL DEPOT")
        print(f"Optimal Tonnage: {x_small.x} tons")
    print(f"Weekly Profit: ${model.objVal}")
    print("-" * 30)