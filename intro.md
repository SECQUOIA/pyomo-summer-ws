# Pyomo Tutorial

Welcome to the *Pyomo Tutorial*. The [SECQUOIA Research Group](https://engineering.purdue.edu/SECQUOIA) maintains these notebooks for learners who want a practical introduction to Python-based mathematical optimization with Pyomo.

The tutorial adapts material from the [Pyomo Summer Workshop 2018](http://www.pyomo.org/workshop-examples) and updates it for current Python and Pyomo workflows. It is designed for workshops, classroom use, and self-study.

## Recommended path

[Pyomo](https://en.wikipedia.org/wiki/Pyomo) is a complete and versatile mathematical optimization package for the Python ecosystem. Pyomo provides a means to build models for optimization using the concepts of decision variables, constraints, and objectives from mathematical optimization, then transform and generate solutions using open source or commercial solvers.

Start with [Python Basics](/notebooks/python/python-exercises.ipynb), then continue into the Pyomo modeling chapters. Python Basics covers the language patterns used later in the optimization examples, Pyomo Fundamentals introduces modeling components and mixed-integer examples, and Pyomo Nonlinear Problems covers nonlinear models and solver behavior.

## Prerequisites

All notebooks in this repository can be opened and run in Google Colab. A launch icon appearing at the top of a page (look for the rocket) indicates the notebook can be opened as an executable document. Selecting Colab will reopen the notebook in Google Colab. Cells inside of the notebooks will perform any necessary installations of Pyomo and solvers needed to execute the code within the notebook.

For local use, install the documentation environment with `uv`. The examples use Pyomo; some solver examples require GLPK or IPOPT to be available in the active environment.

## Feedback

We welcome reports about content bugs, broken links, solver/runtime failures, and teaching feedback. Please [open an issue](https://github.com/SECQUOIA/pyomo-summer-ws/issues/new) with the page, section, and command or notebook cell that produced the problem.

## Credits

The [SECQUOIA Research Group](https://engineering.purdue.edu/SECQUOIA) develops these materials for classroom teaching and for learners entering the world of mathematical programming.

Individual contributors include David Bernal, Zedong Peng, Hamta Bardool, and Albert Lee.
