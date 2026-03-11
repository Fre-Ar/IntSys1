import gurobipy as gp
from gurobipy import GRB
import random
import math

# ==========================================
# TOGGLES & PARAMETERS
# ==========================================
force_infeasible = False 

# Change these numbers to whatever you want! The capacities will automatically adjust.
num_warehouses = 2 #100   # Increase this to make the tree larger
num_customers = 5 #15000 # Increase this to make the matrix larger

# ==========================================
# GENERATE DYNAMIC DATA
# ==========================================
random.seed(42) # Keeps the randomness the same every time you run it

# Coordinates
wh_coords = {i: (random.uniform(0, 100), random.uniform(0, 100)) for i in range(num_warehouses)}
cust_coords = {j: (random.uniform(0, 100), random.uniform(0, 100)) for j in range(num_customers)}

# Calculate shipping costs 
shipping_cost = {}
for i in range(num_warehouses):
    for j in range(num_customers):
        dist = math.hypot(wh_coords[i][0] - cust_coords[j][0], wh_coords[i][1] - cust_coords[j][1])
        shipping_cost[i, j] = dist * 0.5 

# Fixed costs
fixed_costs = {i: random.uniform(10000, 25000) for i in range(num_warehouses)}

# --- DYNAMIC CAPACITY GENERATION ---
# 1. Generate Demand first
demand = {j: random.randint(5, 20) for j in range(num_customers)}
total_demand = sum(demand.values())

# 2. Assign Capacity based on Demand
if force_infeasible:
    # Intentionally make total capacity only 50% of what is needed
    avg_cap_needed = (total_demand * 0.5) / num_warehouses
    wh_capacities = {i: max(1, int(random.uniform(avg_cap_needed * 0.8, avg_cap_needed * 1.2))) for i in range(num_warehouses)} 
else:
    # Normal: Make total capacity 2.5x the total demand (plenty of room, but forces optimization)
    slack_factor = 2.5
    avg_cap_needed = (total_demand * slack_factor) / num_warehouses
    wh_capacities = {i: int(random.uniform(avg_cap_needed * 0.8, avg_cap_needed * 1.2)) for i in range(num_warehouses)}

print(f"Total Customers: {num_customers}")
print(f"Total Warehouses: {num_warehouses}")
print(f"Total Demand: {total_demand:,} packages")
print(f"Total System Capacity: {sum(wh_capacities.values()):,} packages\n")

# ==========================================
# 3. INITIALIZE THE GUROBI MODEL
# ==========================================
model = gp.Model("ECommerce_Network_Tutorial")

# Stop the solver after 30 seconds to show the log file
model.Params.TimeLimit = 30.0  
model.Params.MIPGap = 0.02   
model.Params.LogFile = "classroom_tutorial.log" 

# ==========================================
# 4. DECISION VARIABLES
# ==========================================
y = model.addVars(num_warehouses, vtype=GRB.BINARY, name="Open_WH")
x = model.addVars(num_warehouses, num_customers, lb=0, vtype=GRB.CONTINUOUS, name="Ship")

# ==========================================
# 5. OBJECTIVE FUNCTION
# ==========================================
total_fixed_cost = gp.quicksum(fixed_costs[i] * y[i] for i in range(num_warehouses))
total_ship_cost = gp.quicksum(shipping_cost[i, j] * x[i, j] for i in range(num_warehouses) for j in range(num_customers))

model.setObjective(total_fixed_cost + total_ship_cost, GRB.MINIMIZE)

# ==========================================
# 6. CONSTRAINTS
# ==========================================
for j in range(num_customers):
    model.addConstr(gp.quicksum(x[i, j] for i in range(num_warehouses)) == demand[j], name=f"Demand_Cust_{j}")

for i in range(num_warehouses):
    model.addConstr(gp.quicksum(x[i, j] for j in range(num_customers)) <= wh_capacities[i] * y[i], name=f"Capacity_WH_{i}")

# ==========================================
# 7. OPTIMIZE AND HANDLE RESULTS
# ==========================================
print("Starting the optimization engine...\n" + "-"*40)
model.write("ecommerce_model.lp")
model.optimize()
print("-"*40 + "\n")

if model.status == GRB.OPTIMAL:
    print("SUCCESS: Found the optimal mathematical solution!")
    print(f"Total Minimum Cost: ${model.objVal:,.2f}")

elif model.status == GRB.TIME_LIMIT:
    print("TIME LIMIT REACHED: The solver was stopped early.")
    print(f"Best solution found so far: ${model.objVal:,.2f}")
    print(f"Theoretical best possible: ${model.ObjBound:,.2f}")
    print(f"We are within {model.MIPGap * 100:.2f}% of perfection.")

elif model.status == GRB.INFEASIBLE:
    print("CRITICAL ERROR: The model is mathematically impossible (Infeasible).")
    print("Running computeIIS() to find the contradicting constraints...")
    model.computeIIS()
    model.write("broken_logic.ilp")
    print("\nCheck the 'broken_logic.ilp' file.")

if model.status in [GRB.OPTIMAL, GRB.TIME_LIMIT]:
    open_wh_count = sum(1 for i in range(num_warehouses) if y[i].x > 0.5)
    print(f"\nDecision: We decided to open {open_wh_count} out of {num_warehouses} potential warehouses.")