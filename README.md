# MelodieTable
[![Tests](https://github.com/ABM4ALL/MelodieTable/actions/workflows/test.yml/badge.svg)](https://github.com/ABM4ALL/MelodieTable/actions/workflows/test.yml)
## Introduction
MelodieTable is a pure-python, light-weight and JIT-friendly table library.
It works on CPython3, PyPy and many other third-party interpreters. 
Especially, for third-party interpreters with JIT onboard, MelodieTable will 
take advantage of the JIT for optimal performance.

## Installation
To install it, simply use

```sh
pip install MelodieTable
```


## What is JIT
Python, and all other interpreted languages are slow by nature, because 
interpreter, always considered as a virtual CPU, cannot run as fast as the 
physical CPU. Generally, if no acceleration method adapted, interpreted 
languages can be 10~100x slower than the same algorithm written in 
compiled languages.

Just-In-Time Compilation(JIT) is a widely-used way to improve the speed of 
interpreted languages programs. It compiles dynamically interpreted code into 
binary machine code, making your code faster. Unluckily, CPython interpreter 
does not have embedded JIT system, but a lot of third-party implementations 
does, such as PyPy, GraalPython and RustPython. For this project, currently 
we use PyPy as the standard JIT-ted interpreter

## Why This Library
Pandas is an awesome project for data-analysis under CPython. However, it is 
not the same effective on PyPy, even 2~10x slower. 
If your project chooses PyPy as the interpreter and should handle something 
about tabular data, this library provides an efficient alternative. For many 
common usages, on PyPy, it could outperform CPython+Pandas.

## Principle
MelodieTable is mainly designed according to the following principles:
- Avoid frequent Python-C API operations. 
- Avoid mixing native and 3rd-party types (eg. `np.int` and `int`).
- Make full use of JIT.

To obey these principles, MelodieTable mainly used the following two methods:
- Forced type assertion to make sure table data are all native types. 
- Dynamic code generation, which generates optimized code for some specified table 
operations.
