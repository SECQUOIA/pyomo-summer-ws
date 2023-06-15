# rosenbrock_script_loop.py: A Pyomo model for the Rosenbrock problem
from pyomo.environ import *

model = ConcreteModel()
model.x = Var()
model.y = Var()

def rosenbrock(m):
    return (1.0-m.x)**2 + 100.0*(m.y - m.x**2)**2
model.obj = Objective(rule=rosenbrock, sense=minimize)


solver = SolverFactory('ipopt')

print('x_init, y_init, x_soln, y_soln')
y_init = 5.0
for x_init in range(2, 6):
    model.x = x_init
    model.y = 5.0

    solver.solve(model)

    print("{0:6.2f}  {1:6.2f}  {2:6.2f}  {3:6.2f}".format(x_init, \
            y_init, value(model.x), value(model.y)))
    
