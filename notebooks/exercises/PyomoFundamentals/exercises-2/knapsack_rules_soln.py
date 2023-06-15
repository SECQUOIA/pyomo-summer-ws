from pyomo.environ import *

A = ['hammer', 'wrench', 'screwdriver', 'towel']
b = {'hammer':8, 'wrench':3, 'screwdriver':6, 'towel':11}
w = {'hammer':5, 'wrench':7, 'screwdriver':4, 'towel':3}
W_max = 14

model = ConcreteModel()
model.x = Var( A, within=Binary )

def obj_rule(m):
    return sum( b[i]*m.x[i] for i in A )
model.obj = Objective(rule=obj_rule, sense = maximize )

def weight_con_rule(m):
    return sum( w[i]*m.x[i] for i in A ) <= W_max
model.weight_con = Constraint(rule=weight_con_rule)

opt = SolverFactory('glpk')
opt_success = opt.solve(model)

model.pprint()

