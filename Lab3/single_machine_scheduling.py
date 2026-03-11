import gurobipy as gp
from gurobipy import GRB

# DATA
# Processing times (p_j) and release times (r_j) for 6 jobs
jobs = range(6)
p = {0: 3, 1: 5, 2: 2, 3: 4, 4: 6, 5: 3}
r = {0: 0, 1: 2, 2: 5, 3: 3, 4: 1, 5: 4} 
# UPDATE THE RELEASE TIME OF THE LATEST JOB IN THE OPTIMAL SOLUTION TO A LARGE VALUE AND OBSERVE THE SOLUTION
# UPDATE THE RELEASE TIMES AND MAKE THEM ALL 0 AND REMOVE EITHER-OR CONSTRAINTS, OBSERVE THE SOLUTION

# Big M should be larger than any possible completion time
M = sum(p.values()) + max(r.values())

model = gp.Model("Single_Machine_Scheduling")

# DECISION VARIABLES
# s[j]: starting time of job j
s = model.addVars(jobs, lb=0, vtype=GRB.CONTINUOUS, name="s")

# y[i,j]: binary variable; 1 if job i precedes job j, 0 otherwise
y = model.addVars(jobs, jobs, vtype=GRB.BINARY, name="y")

# C_max: The makespan (time the last job finishes)
C_max = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="makespan")

# CONSTRAINTS
# Release time constraint: s_j >= r_j
for j in jobs:
    model.addConstr(s[j] >= r[j], name=f"Release_{j}")

# Disjunctive (Either-Or) constraints: prevent job overlap
# For every pair of jobs (i, j) where i < j:
for i in jobs:
    for j in jobs:
        if i < j: # REMOVE THIS OR MAKE IT != TO OBSERVE HOW THE SOLUTION CHANGES OR THE NUMBER OF CONSTRAINTS
            # Either i before j: s_i + p_i <= s_j
            model.addConstr(s[i] + p[i] <= s[j] + M * (1 - y[i, j]), name=f"Seq_ij_{i}_{j}")
            # Or j before i: s_j + p_j <= s_i
            model.addConstr(s[j] + p[j] <= s[i] + M * y[i, j], name=f"Seq_ji_{i}_{j}")

# Makespan definition: C_max >= s_j + p_j for all jobs
for j in jobs:
    model.addConstr(C_max >= s[j] + p[j], name=f"Cmax_def_{j}")

# OBJECTIVE
model.setObjective(C_max, GRB.MINIMIZE)

# SOLVE
model.optimize()

# OUTPUT RESULTS
if model.status == GRB.OPTIMAL:
    print(f"\nOptimal Makespan: {model.objVal}")
    # Sort jobs by start time for clarity
    schedule = sorted(jobs, key=lambda j: s[j].x)
    print("Job Schedule:")
    for j in schedule:
        print(f"Job {j}: Starts at {s[j].x:.1f}, Finishes at {s[j].x + p[j]:.1f}")