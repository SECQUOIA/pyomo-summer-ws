from pyomo.environ import *

A = ['hammer', 'wrench', 'screwdriver', 'towel']
b = {'hammer':8, 'wrench':8, 'screwdriver':6, 'towel':11}
w = {'hammer':5, 'wrench':7, 'screwdriver':4, 'towel':3}
W_max = 14

model = ConcreteModel()
model.x = Var( A, within=Binary )

model.obj = Objective(
    expr = sum( b[i]*model.x[i] for i in A ), 
    sense = maximize )

model.weight_con = Constraint(
    expr = sum( w[i]*model.x[i] for i in A ) <= W_max )

opt = SolverFactory('glpk')
opt_success = opt.solve(model)

total_weight = sum( w[i]*value(model.x[i]) for i in A )
print('Total Weight:', total_weight)
print('Total Benefit:', value(model.obj))

print('%12s %12s' % ('Item', 'Selected'))
print('=========================')
for i in A:
    acquired = 'No'
    if value(model.x[i]) >= 0.5:
        acquired = 'Yes'
    print('%12s %12s' % (i, acquired))
print('-------------------------')
