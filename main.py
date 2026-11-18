from plot import Plot, Parameter
from lattice import IsingLattice, XYLattice

lattice = IsingLattice(500, 300)

plot = Plot((1500, 900), lattice)

plot.add_parameter(Parameter("B", -2, 2, 0))
plot.add_parameter(Parameter("J", -1, 1, 1))
plot.add_parameter(Parameter("T", 0.01, 5, 2.1))

plot.run()

# lattice = XYLattice(100, 50)

# plot = Plot((1500, 900), lattice)

# plot.add_parameter(Parameter("T", 0, 2, 0))
# plot.add_parameter(Parameter("delta", 0, 1, 0))

# plot.run()