# MelodieTable
MelodieTable is a pure-python table used in Melodie, an ABM framework. It is mainly used in the following aspects:
- Avoid frequent Python-C API operations. 
- Avoid mixing native and 3rd-party types. 

For general CPython interpreters, arithmic calculation between numpy/pandas types and native types can be costly. On PyPy interpreters, C-API was implemented by interpretation, so the C-API is much slower than that on CPython. As a result, pandas on PyPy was 3~5 times slower.

This repo is aimed at creating a light-weight table class, to make simple table operations like querying or indicing on PyPy faster than simple pandas operations.

这个仓库可以避免Pandas过度调用Python的C-API，从而避免在PyPy解释器引入Pandas之后速度远远慢于CPython的情形。

