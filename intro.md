# Pyomo Tutorial

Welcome to the *Pyomo Tutorial*. The [SECQUOIA Research Group](https://engineering.purdue.edu/SECQUOIA) maintains these notebooks for learners who want a practical introduction to Python-based mathematical optimization with Pyomo.

The tutorial adapts material from the [Pyomo Summer Workshop 2018](http://www.pyomo.org/workshop-examples) and updates it for current Python and Pyomo workflows. It is designed for workshops, classroom use, and self-study.

## Recommended path

[Pyomo](https://en.wikipedia.org/wiki/Pyomo) is a complete and versatile mathematical optimization package for the Python ecosystem. Pyomo provides a means to build models for optimization using the concepts of decision variables, constraints, and objectives from mathematical optimization, then transform and generate solutions using open source or commercial solvers.

Start with [Python Basics](/notebooks/01-python-basics/python-exercises.ipynb), then continue into the Pyomo modeling chapters. Python Basics covers the language patterns used later in the optimization examples, Pyomo Fundamentals introduces modeling components and mixed-integer examples, and Pyomo Nonlinear Problems covers nonlinear models and solver behavior.

## Learning objectives

After completing the tutorial, you should be able to:

- use core Python data structures and control flow in modeling scripts;
- formulate Pyomo variables, objectives, constraints, sets, and parameters;
- solve linear, mixed-integer, and nonlinear Pyomo models with appropriate solvers;
- diagnose common modeling and solver failures;
- adapt the examples for new classroom or self-study exercises.

## Prerequisites

All notebooks in this repository can be opened and run in Google Colab from direct links on each notebook page. For local use, install the documentation environment with `uv`. The examples use Pyomo; some solver examples require GLPK or IPOPT to be available in the active environment.

See [Setup and Solvers](/setup.md) for local preview commands, Colab links, and solver installation notes.

## Feedback

We welcome reports about content bugs, broken links, solver/runtime failures, and teaching feedback. Please [open an issue](https://github.com/SECQUOIA/pyomo-summer-ws/issues/new/choose) with the page, section, and command or notebook cell that produced the problem.

## Credits

The [SECQUOIA Research Group](https://engineering.purdue.edu/SECQUOIA) develops these materials for classroom teaching and for learners entering the world of mathematical programming.

Individual contributors include David Bernal, Zedong Peng, Hamta Bardool, and Albert Lee.

These materials adapt the public Pyomo workshop examples and Pyomo modeling references. Notebook-specific references appear in the relevant chapters.
