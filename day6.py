#!/usr/bin/env python3

"""
Advent of Code 2023, day 6: Wait For It

Reduce problem to solving a quadratic equation.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, math

def distFn(charge_time, time_avail):
  """
  Returns the distance traveled in (time_avail-charge_time) with
  speed charge_time.

  d = c * (t-c) = -c^2 + t*c
  """
  if charge_time <= 0 or charge_time >= time_avail:
    return 0

  return (time_avail - charge_time) * charge_time


def countWinnable(time, dist_to_beat):
  wins = 0
  for charge_time in range(1, time):
    dist = distFn(charge_time, time)
    if dist > dist_to_beat:
      wins += 1
    # print(f'{charge_time:4}ms: {dist}mm')
  return wins


def part1(filename):
  with open(filename) as inf:
    time_line = inf.readline().split()
    assert time_line[0] == 'Time:'
    times = [int(x) for x in time_line[1:]]

    dist_line = inf.readline().split()
    assert dist_line[0] == 'Distance:'
    dists = [int(x) for x in dist_line[1:]]

  assert len(times) == len(dists)

  product = 1
  for i in range(len(times)):
    time = times[i]
    dist_to_beat = dists[i]
    wins = countWinnable(time, dist_to_beat)
    # print(f'Given {time} ms, beat {dist_to_beat} mm {wins} ways')
    product *= wins
  print(f'part1 {product}')


def part2(filename):
  with open(filename) as inf:
    time_line = inf.readline().split()
    assert time_line[0] == 'Time:'
    time = int(''.join(time_line[1:]))

    dist_line = inf.readline().split()
    assert dist_line[0] == 'Distance:'
    dist_to_beat = int(''.join(dist_line[1:]))

  """
  x = charge time
  b = time available
  d = distance traveled

  d = x * (b-x)
    = -x**2 + b*x

  c = -(previous best)

  to beat the previous best, d must be greater than b
  -x**2 + b*x > -c
  -x**2 + b*x + c > 0

  quadratic formula: roots = (-b +- sqrt(b**2 - 4 a c)) / (2a)
  in this formula a = -1, so the beginning of the range in which
  we can be the previous best time is:
    ceiling( (-b + sqrt(b**2 - 4 a c)) / (2a) )
    or
    math.ceil( (-b + math.sqrt(b**2 - 4 * a * c)) / (2*a) )
  and the end of the range:
    floor( (-b - sqrt(b**2 - 4 a c)) / (2a) )
    or
    math.floor( (-b - math.sqrt(b**2 - 4 * a * c)) / (2*a) )
  
  11200894.3465948
  48487379.653405204

  >>> 48487379 - 11200895 + 1
  37286485
  
  """

  a = -1
  b = time
  c = -dist_to_beat
  lo = math.ceil( (-b + math.sqrt(b**2 - 4 * a * c)) / (2*a) )
  hi = math.floor( (-b - math.sqrt(b**2 - 4 * a * c)) / (2*a) )
  print(f'part2 {hi - lo + 1}')
  

if __name__ == '__main__':
  filename = 'day6.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
