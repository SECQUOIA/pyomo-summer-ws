from pyomo.environ import *
from pyomo.dae import *

model = m = ConcreteModel()

m.t = ContinuousSet(bounds=(0,1))

m.z = Var(m.t)
m.dzdt = DerivativeVar(m.z)

m.obj = Objective(expr=1) # Dummy Objective

def _zdot(m, i):
    return m.dzdt[i] == m.z[i]**2 - 2*m.z[i] +1
m.zdot = Constraint(m.t,rule=_zdot)

def _init_con(m):
    return m.z[0] == -3
m.init_con = Constraint(rule=_init_con)

# Discretize using backward finite difference
#discretizer = TransformationFactory('dae.finite_difference')
#discretizer.apply_to(m, nfe=50, scheme='BACKWARD')

# Discretize using collocation
discretizer = TransformationFactory('dae.collocation')
discretizer.apply_to(m, nfe=2, ncp=3 , scheme='LAGRANGE-RADAU')


solver = SolverFactory('ipopt')
solver.solve(m,tee=True)

import matplotlib.pyplot as plt

analytical_t = [0.01*i for i in range(0,101)]
analytical_z = [(4*t-3)/(4*t+1) for t in analytical_t]

findiff_t = list(m.t)
findiff_z = [value(m.z[i]) for i in m.t]

plt.plot(analytical_t,analytical_z,'b',label='analytical solution')
plt.plot(findiff_t,findiff_z,'ro--',label='pyomo.dae discretization solution')
plt.legend(loc='best')
plt.xlabel('t')
plt.show()
