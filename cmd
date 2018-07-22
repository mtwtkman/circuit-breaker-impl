#! /bin/sh

. v/bin/activate

case $1 in
  t) v/bin/python -m unittest tests;;
  tp) v/bin/python -m unittest tests.CircuitBreakerTest.test_$2;;
  i) v/bin/python setup.py install;;
  r) rm -rf build *.egg-info dist;;
esac
