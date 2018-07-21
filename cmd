#! /bin/sh

case $1 in
  t) v/bin/python -m unittest tests;;
  tp) v/bin/python -m unittest tests.CircuitBreakerTest.test_$2;;
esac
