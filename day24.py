#!/usr/bin/env python3

"""
Advent of Code 2023, day 24: Never Tell Me The Odds

Solving systems of equations.

I took the lazy way out on part 2. Rather than solving the
system of equations directly, I output them as Mathematica input,
then used that to solve for the necessary variables.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, re, collections, math
from fractions import Fraction


line_re = re.compile(r'(\d+), *(\d+), *(\d+) *@ *(-?\d+), *(-?\d+), *(-?\d+)')


def vectorStr(vector):
  return '(' + ','.join([str(i) for i in vector]) + ')'


def similar(a, b):
  return abs(a-b) < .001

class Beam:
  def __init__(self, line):
    match = line_re.search(line)
    if not match:
      print('Error, bad input line: ' + line)
      return
    self.pos = [int(x) for x in match.groups()[:3]]
    self.vec = [int(x) for x in match.groups()[3:]]

  def __str__(self):
    return f'position{vectorStr(self.pos)}, velocity{vectorStr(self.vec)}'

  def apply(self, time):
    return tuple(pos + time * vec for (pos,vec) in zip(self.pos, self.vec))
    # return (self.x + time * self.dx,
    #         self.y + time * self.dy,
    #         self.z + time * self.dz)

  def isParallel_2d(self, that):
    v1 = self.vec
    v2 = that.vec
    factor = None

    for v1, v2 in zip(self.vec[:2], that.vec[:2]):
      if v2 != 0:
        if factor == None:
          factor = Fraction(v1, v2)
        else:
          if factor != Fraction(v1, v2):
            return False
      else:
        if v1 != 0: return False

    return True
          

def readInput(inf):
  beams = []
  for line in inf:
    beams.append(Beam(line))
  return beams

def intersectTimes(b1, b2):
  """
  Return (t1, t2) such that b1.apply(t1) == b2.apply(t2).
  If no such values exist (b1 and b2 are parallel), return (None, None)
  """
  if b1.isParallel_2d(b2):
    return None,None

  try:
    # I derived these formulas by manually solving the system of equations:
    # b1.pos + t1 * b1.vec == b2.pos + t2 * b2.vec
    # The Fraction class is helpful to avoid floating point rounding errors, since it
    # only does integer arithmetic.
    # t2 = ( (b2.pos[1] - b1.pos[1]) * b1.vec[0] - (b2.pos[0] - b1.pos[0]) * b1.vec[1] ) / (b2.vec[0] * b1.vec[1] - b2.vec[1] * b1.vec[0])
    t2 = Fraction((b2.pos[1] - b1.pos[1]) * b1.vec[0] - (b2.pos[0] - b1.pos[0]) * b1.vec[1], 
                  b2.vec[0] * b1.vec[1] - b2.vec[1] * b1.vec[0])
    # t1 = (b2.pos[0] - b1.pos[0] + t2 * b2.vec[0]) / b1.vec[0]
    t1 = Fraction(b2.pos[0] - b1.pos[0] + t2 * b2.vec[0], b1.vec[0])

    return t1, t2
  except ZeroDivisionError as e:
    print(f'ZeroDivisionError with\n  {b1}\n  {b2}')
    assert False
  

def part1(beams):
  # for beam in beams:
  #   print(beam)

  intersections = 0
  for i, b1 in enumerate(beams):
    for j in range(i+1, len(beams)):
      b2 = beams[j]
      # print(f'{i} x {j}')
      t1,t2 = intersectTimes(b1, b2)
      if t1 == None or t2 == None:
        # print('  parallel')
        continue
      if t1 < 0 or t2 < 0:
        # print('  insersection(s) in the past')
        continue
      p1 = b1.apply(t1)
      if (200000000000000 <= p1[0] <= 400000000000000 and
          200000000000000 <= p1[1] <= 400000000000000 ):
        # print('  intersect in range')
        intersections += 1
      else:
        # print('  not in range')
        pass
      
      # p2 = b2.apply(t2)

      # print(f'  beam[{i}]({t1}) = {p1[0]},{p1[1]}')
      # print(f'  beam[{j}]({t2}) = {p2[0]},{p2[1]}')
      # t1 = float(t1)
      # t2 = float(t2)
      # p1 = [float(x) for x in p1]
      # p2 = [float(x) for x in p2]
      # print(f'  beam[{i}]({t1:.3f}) = {p1[0]:.3f},{p1[1]:.3f}')
      # print(f'  beam[{j}]({t2:.3f}) = {p2[0]:.3f},{p2[1]:.3f}')

  print(f'part1 {intersections}')


def part2(beams):
  # 300 beams
  """
  The rock has to hit each hailstone, so the time for both equations is
  the same.
  Let the starting position be x, y, z, and vector vx, vy, vz.
  The hailstones are (x1..x300, y1..y300, z1..z300), (vx1..vx300, ...)
  The times our rock will hit the hailstones are t1..t300.

  With D dimensions and N hailstones, there are 2D+N unknowns and
  D*N equations.

  Fix D at 3.
  With N hailstones there are 6+N unknowns and 3N equations.
  With N=3 there are 9 of each. So for N<3 the system is under-constrained
  and N>3 over-constrained. This means that we don't have to solve for
  all 300 hailstones, just the first 3.

  If it was a system of linear equations I'd put them into a matrix and
  use numpy to solve them, but they're nonlinear. There may be a way to solve
  that with numpy, but I've got a copy of Mathematica, and it had no problem
  solving it. So, this code outputs the problem in Mathematica code, which
  I pasted into Mathematica so solve it.
  """

  dims = ['x', 'y', 'z']
  print('Solve[{')
  for i, beam in enumerate(beams[:3]):
    for j, dim in enumerate(['x', 'y', 'z']):
      suffix = '' if i==2 and dim=='z' else ','
      print(f'  {beam.pos[j]} + t{i} * {beam.vec[j]} == {dim} + t{i} * v{dim}{suffix}')
      
  print('}, {x, y, z, vx, vy, vz, t0, t1, t2}]')

  """
  solutions, courtesy of Mathematica:
    x -> 354954946036320
    y -> 318916597757112
    z -> 112745502066835
    vx -> -117
    vy -> -69
    vz -> 281
    t0 -> 201366111929
    t1 -> 268172080425
    t2 -> 250545362574
  """

  x = 354954946036320
  y = 318916597757112
  z = 112745502066835
  print(f'part2 {x+y+z}')


if __name__ == '__main__':
  filename = 'day24.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  with open(filename) as inf:
    beams = readInput(inf)
  part1(beams)
  part2(beams)
  
