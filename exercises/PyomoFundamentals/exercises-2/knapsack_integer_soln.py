from pyomo.environ import *

A = ['hammer', 'wrench', 'screwdriver', 'towel']
b = {'hammer':8, 'wrench':3, 'screwdriver':6, 'towel':11}
w = {'hammer':5, 'wrench':7, 'screwdriver':4, 'towel':3}
W_max = 14
N = range(6) # create a list from 0-5

model = ConcreteModel()
model.x = Var( A )
model.q = Var( A, N, within=Binary )

def obj_rule(m):
    return sum( b[i]*m.x[i] for i in A )
model.obj = Objective(rule=obj_rule, sense = maximize )

def weight_con_rule(m):
    return sum( w[i]*m.x[i] for i in A ) <= W_max
model.weight_con = Constraint(rule=weight_con_rule)

def x_integer_rule(m, i):
    return m.x[i] == sum( j*m.q[i,j] for j in N )
model.x_integer = Constraint(A, rule=x_integer_rule)

opt = SolverFactory('glpk')
result_obj = opt.solve(model)

total_weight = sum( w[i]*value(model.x[i]) for i in A )
print('Total Weight:', total_weight)
print('Total Benefit:', value(model.obj))

print('%12s %12s' % ('Item', '# Selected'))
print('=========================')
for i in A:
    print('%12s %12s' % (i, value(model.x[i])))
print('-------------------------')


