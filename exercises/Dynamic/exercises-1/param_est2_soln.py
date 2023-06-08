from pyomo.environ import *
from pyomo.dae import *

a_conc = {0.1:0.606, 0.2:0.368, 0.3:0.223, 0.4:0.135, 0.5:0.082,
          0.6:0.05, 0.7:0.03, 0.8:0.018, 0.9:0.011, 1.0:0.007}

b_conc = {0.1:0.373, 0.2:0.564, 0.3:0.647, 0.4:0.669, 0.5:0.656,
          0.6:0.624, 0.7:0.583, 0.8:0.539, 0.9:0.494, 1.0:0.451}

m = ConcreteModel()

m.meas_time = Set(initialize=sorted(a_conc.keys()),ordered=True)
m.ameas = Param(m.meas_time, initialize=a_conc)
m.bmeas = Param(m.meas_time, initialize=b_conc)

m.time = ContinuousSet(initialize=m.meas_time, bounds=(0,1))

m.a = Var(m.time, bounds=(0,1))
m.b = Var(m.time, bounds=(0,1))

m.dadt = DerivativeVar(m.a)
m.dbdt = DerivativeVar(m.b)

m.k1 = Var()
m.k2 = Var()

def _a_diffeq(m,t):
    return m.dadt[t] == -m.k1*m.a[t]
m.a_diffeq = Constraint(m.time, rule=_a_diffeq)

def _b_diffeq(m,t):
    return m.dbdt[t] == m.k1*m.a[t] - m.k2*m.b[t]
m.b_diffeq = Constraint(m.time, rule=_b_diffeq)

m.ainit = Constraint(expr=m.a[0]==1)
m.binit = Constraint(expr=m.b[0]==0)

def _obj(m):
    return sum((m.a[t]-m.ameas[t])**2+(m.b[t]-m.bmeas[t])**2 for t in m.meas_time)
m.obj = Objective(rule=_obj)

discretizer = TransformationFactory('dae.collocation')
discretizer.apply_to(m,nfe=10,ncp=3,scheme='LAGRANGE-RADAU')

solver = SolverFactory('ipopt')
solver.solve(m, tee=True)

print('k1= '+str(value(m.k1)))
print('k2= '+str(value(m.k2)))

meas_time = list(m.meas_time)
a_meas = [value(m.ameas[i]) for i in m.meas_time]
b_meas = [value(m.bmeas[i]) for i in m.meas_time]

t = list(m.time)
a = [value(m.a[i]) for i in m.time]
b = [value(m.b[i]) for i in m.time]
    
import matplotlib.pyplot as plt

plt.plot(t,a,label='A')
plt.plot(t,b,label='B')
plt.plot(meas_time,a_meas,'o')
plt.plot(meas_time,b_meas,'o')
plt.legend(loc='best')
plt.xlabel('t')
plt.ylabel('concentration')
plt.title('Kinetic Parameter Estimation')
plt.show()
