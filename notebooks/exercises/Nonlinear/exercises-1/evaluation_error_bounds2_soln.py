from pyomo.environ import *

model = ConcreteModel()

model.x = Var(initialize=5.0, bounds=(1.001,None))
model.y = Var(initialize=5.0)

def obj_rule(m):
    return (m.x-1.01)**2 + m.y**2
model.obj = Objective(rule=obj_rule)

def con_rule(m):
    return m.y == sqrt(m.x - 1.0)
model.con = Constraint(rule=con_rule)

solver = SolverFactory('ipopt')
solver.options['halt_on_ampl_error'] = 'yes'
solver.solve(model, tee=True)

print( value(model.x) )
print( value(model.y) )
