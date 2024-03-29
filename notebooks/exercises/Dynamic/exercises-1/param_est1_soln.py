#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

# Sample Problem 2: Parameter Estimation
# (Ex 5 from Dynopt Guide)
#
#	min sum((X1(ti)-X1_meas(ti))^2)
#	s.t.	X1_dot = X2			X1(0) = p1
#		X2_dot = 1-2*X2-X1		X2(0) = p2
#		-1.5 <= p1,p2 <= 1.5
#		tf = 6
#

from pyomo.environ import *
from pyomo.dae import *

measurements = {1:0.264, 2:0.594, 3:0.801, 5:0.959}

model = ConcreteModel()
model.t = ContinuousSet(initialize=measurements.keys(),bounds=(0, 6))	

model.x1 = Var(model.t)
model.x2 = Var(model.t)

model.p1 = Var(bounds=(-1.5,1.5))
model.p2 = Var(bounds=(-1.5,1.5))

model.x1dot = DerivativeVar(model.x1,wrt=model.t)
model.x2dot = DerivativeVar(model.x2)

def _init_conditions(model):
	yield model.x1[0] == model.p1
	yield model.x2[0] == model.p2
model.init_conditions = ConstraintList(rule=_init_conditions)

# Alternate way to declare initial conditions
#def _initx1(model):
#	return model.x1[0] == model.p1		
#model.initx1 = Constraint(rule=_initx1)

#def _initx2(model):
#	return model.x2[0] == model.p2
#model.initx2 = Constraint(rule=_initx2)

def _x1dot(model,i):
	return model.x1dot[i] == model.x2[i]
model.x1dotcon = Constraint(model.t, rule=_x1dot)

def _x2dot(model,i):
	return model.x2dot[i] == 1-2*model.x2[i]-model.x1[i]
model.x2dotcon = Constraint(model.t, rule=_x2dot)

def _obj(model):
	return sum((model.x1[i]-measurements[i])**2 for i in measurements.keys())
model.obj = Objective(rule=_obj)

# Discretize model using Orthogonal Collocation
discretizer = TransformationFactory('dae.collocation')
discretizer.apply_to(model,nfe=8,ncp=5)

solver=SolverFactory('ipopt')

results = solver.solve(model,tee=True)

t_meas = sorted(list(measurements.keys()))
x1_meas = [value(measurements[i]) for i in sorted(measurements.keys())]

t = list(model.t)
x1 = [value(model.x1[i]) for i in model.t]
    
import matplotlib.pyplot as plt

plt.plot(t,x1)
plt.plot(t_meas,x1_meas,'o')
plt.xlabel('t')
plt.ylabel('x')
plt.title('Dynamic Parameter Estimation Using Collocation')
plt.show()
