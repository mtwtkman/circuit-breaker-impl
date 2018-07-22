#! /bin/sh

. v/bin/activate

case $1 in
  init) pip install bottle setuptools;;
  t) python -m unittest tests;;
  tp) python -m unittest tests.CircuitBreakerTest.test_$2;;
  i) python setup.py install;;
  r) rm -rf build *.egg-info dist;;
esac
