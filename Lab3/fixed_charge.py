import gurobipy as gp
from gurobipy import GRB

# Initialize the model
model = gp.Model("Gandhi_Cloth_Fixed_Charge")

# DATA
products = ['shirts', 'shorts', 'pants']
fixed_costs = {'shirts': 200, 'shorts': 150, 'pants': 100}
sale_price = {'shirts': 12, 'shorts': 8, 'pants': 15}
variable_cost = {'shirts': 6, 'shorts': 4, 'pants': 8}

# Resource requirements
labor_req = {'shirts': 3, 'shorts': 2, 'pants': 6}
cloth_req = {'shirts': 4, 'shorts': 3, 'pants': 4}

# Capacities
labor_limit = 150
cloth_limit = 160

# DECISION VARIABLES
# x[i]: units of product i produced
x = model.addVars(products, vtype=GRB.INTEGER, name="x")
# y[i]: binary variable (1 if machinery is rented, 0 otherwise)
y = model.addVars(products, vtype=GRB.BINARY, name="y")

# OBJECTIVE FUNCTION
# Maximize: sum((Price - VarCost) * x) - sum(FixedCost * y)
obj = gp.quicksum((sale_price[p] - variable_cost[p]) * x[p] for p in products) - \
      gp.quicksum(fixed_costs[p] * y[p] for p in products)
model.setObjective(obj, GRB.MAXIMIZE)

# CONSTRAINTS
# Labor constraint
model.addConstr(gp.quicksum(labor_req[p] * x[p] for p in products) <= labor_limit, "Labor")

# Cloth constraint
model.addConstr(gp.quicksum(cloth_req[p] * x[p] for p in products) <= cloth_limit, "Cloth")

# Fixed-charge logical constraints (Linking constraints)
# Big M: A value large enough that it doesn't limit x, but connects it to y.
# Here, M=100 is safe since cloth/labor limits would prevent x from exceeding this.
M = 100 
for p in products:
    model.addConstr(x[p] <= M * y[p], f"Link_{p}")

# 5. OPTIMIZE
model.optimize()

# 6. OUTPUT RESULTS
if model.status == GRB.OPTIMAL:
    print(f"\nMaximized Weekly Profit: ${model.objVal}")
    for p in products:
        if x[p].x > 0:
            print(f"Produce {int(x[p].x)} {p}")