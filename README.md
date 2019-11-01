# Calculator
[![Build Status](https://travis-ci.com/matthieucham/calculator.svg?branch=master)](https://travis-ci.com/matthieucham/calculator)
[![Coverage Status](https://coveralls.io/repos/github/matthieucham/calculator/badge.svg?branch=master)](https://coveralls.io/github/matthieucham/calculator?branch=master)

Python implementation of command-line calculator for infix math expressions given as string, implementing parsing algorithms from http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
  

## Requirements

* Python (2.7, 3.4, 3.5, 3.6, 3.7)
* No external dependencies !

## Installation

 Just copy the main script **calc.py** to the current folder.
 
 ## Usage
 
 Invoke the calculator with an expression to evaluate:
 
  ``python calc.py '5.6 * 2'``
 
 The expression must be enclosed in simple quotes.
 
 To get full usage details, invoke:
 
 ``python calc.py -h ``
 
 ### Algorithms
 
 By default, the calculator makes use of the **Precedence Climbing** algorithm by Theo Norvell http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
 
 You can switch to the more classic **Shunting Yard** parsing algorithm with the --algo option:
 
  ``python calc.py '5.6 * 2' --algo sh``
 

 ### Supported operators
 - `+` (addition)
 - `-` (subtraction)
 - `*` (multiplication)
 - `/` (division)
 - `^` (power elevation)
 - `-` (unary operator minus)
 
 ### int or float ?
 
Same as Python basic operations behaviour: if the result of the evaluation is an integer, then output an integer, otherwise a float.

 ```
 python calc.py '4 / 2'
 2
 ```
 
 ```
 python calc.py '5 / 2'
 2.5
 ```
 
 ## Run tests
 
 ### With tox
 
 To run the tests suite on all supported Python versions, first install **Tox** in your environment
 
 ``pip install tox``
 
 Then simply run
 
 ``tox``
 
 ### Without tox
 
 Run the full test suite with unittests
 
 ``python -m unittest -v tests`` 
 
 # Acknowledgment
 
 Thanks to Mr Theo Norvell for its precious article "Parsing Expressions by Recursive Descent" http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
