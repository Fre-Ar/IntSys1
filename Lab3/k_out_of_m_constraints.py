import gurobipy as gp
from gurobipy import GRB

# Initialize Model
model = gp.Model("k_out_of_m_Example")

# VARIABLES
# Let's assume two continuous variables x and y
x = model.addVar(name="x")
y = model.addVar(name="y")

# Binary variables: z[i] = 1 if constraint i is RELAXED (need not be satisfied)
# z[i] = 0 if constraint i MUST be satisfied
m = 5
k = 3
z = model.addVars(m, vtype=GRB.BINARY, name="z")

# THE m CONSTRAINTS (f_i(x) <= 0)
# We use a Big M to relax these. If z[i] is 1, the RHS becomes very large, 
# making the constraint trivial to satisfy.
M = 1000 

# Example set of arbitrary constraints:
model.addConstr(2*x + 3*y <= 10 + M * z[0], name="c0")
model.addConstr(x - 4*y   <= 5  + M * z[1], name="c1")
model.addConstr(5*x + y   <= 20 + M * z[2], name="c2")
model.addConstr(-x + 2*y  <= 8  + M * z[3], name="c3")
model.addConstr(x + y     <= 12 + M * z[4], name="c4")

# CHANGE THE DEFINITION FOR z-VARIABLES: z[i] = 1 if constraint i must be satisfied
# AND CHANGE THE SUM CONSTRAINTS (REMOVE THE BELOW ONE IF YOU ACTIVATE THIS)
# model.addConstr(2*x + 3*y <= 10 + M * (1 - z[0]), name="c0")
# model.addConstr(x - 4*y   <= 5  + M * (1 - z[1]), name="c1")
# model.addConstr(5*x + y   <= 20 + M * (1 - z[2]), name="c2")
# model.addConstr(-x + 2*y  <= 8  + M * (1 - z[3]), name="c3")
# model.addConstr(x + y     <= 12 + M * (1 - z[4]), name="c4")
# model.addConstr(gp.quicksum(z[i] for i in range(m)) >= k, name="k_limit")

# THE k-OUT-OF-m LOGIC
# According to the formulation: sum(z_i) <= m - k
# This ensures that at most (m-k) constraints are relaxed, 
# meaning at least k must be satisfied.
model.addConstr(gp.quicksum(z[i] for i in range(m)) <= m - k, name="k_limit")


# OBJECTIVE & SOLVE
# Just an example objective to find a feasible point
model.setObjective(x + y, GRB.MAXIMIZE)
model.optimize()

# OUTPUT RESULTS
if model.status == GRB.OPTIMAL:
    print(f"x value = {x.x}")
    print(f"y value = {y.x}")
    print(f"z values:")
    for i in range(m):
        print(f"z_{i} = {z[i].x}")