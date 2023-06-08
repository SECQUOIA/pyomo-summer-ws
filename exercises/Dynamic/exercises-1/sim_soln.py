from pyomo.environ import *
from pyomo.dae import *

m = ConcreteModel()

m.t = ContinuousSet(bounds=(0,1))
m.a = Var(m.t)
m.b = Var(m.t)

m.k1 = Param(initialize=5)
m.k2 = Param(initialize=1)

m.dadt = DerivativeVar(m.a)
m.dbdt = DerivativeVar(m.b)

m.a[0].fix(1)
m.b[0].fix(0)

def _da(m, t):
    return m.dadt[t] == -m.k1*m.a[t]
m.da_con = Constraint(m.t, rule=_da)

def _db(m, t):
    return m.dbdt[t] == m.k1*m.a[t] - m.k2*m.b[t]
m.db_con = Constraint(m.t, rule=_db)

mysim = Simulator(m, package='scipy')
tsim, profiles = mysim.simulate(integrator='vode', numpoints=100)

import matplotlib.pyplot as plt

varorder = mysim.get_variable_order()
for idx, v in enumerate(varorder):
    plt.plot(tsim, profiles[:, idx], label=v)

plt.xlabel('t')
plt.legend(loc='best')
plt.show()

plt.show()
