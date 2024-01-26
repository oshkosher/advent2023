#!/usr/bin/env python3

"""
Advent of Code 2023, day 24: Never Tell Me The Odds

Solving systems of equations.

My solution for part 2 uses the sympy symbolic math library to solve
a system of equations, so to run it you'll need to install that.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, re, collections, math, time
from fractions import Fraction
import sympy


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
  If no such value exit (b1 and b2 are parallel), return (None, None)
  """
  if b1.isParallel_2d(b2):
    return None,None

  try:
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


def part2WriteMathematicaInput(beams):
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

  for i, beam in enumerate(beams[:3]):
    for j, dim in enumerate(['x', 'y', 'z']):
      print(f'{dim}{i} = {beam.pos[j]};')
      print(f'd{dim}{i} = {beam.vec[j]};')

  print('Solve[{')
  for i, beam in enumerate(beams[:3]):
    for j, dim in enumerate(['x', 'y', 'z']):
      suffix = '' if i==2 and dim=='z' else ','
      # print(f'  {beam.pos[j]} + t{i} * {beam.vec[j]} == {dim} + t{i} * v{dim}{suffix}')
      print(f'  {dim}{i} + t{i} * d{dim}{i} == {dim} + t{i} * d{dim}{suffix}')
      
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


def part2sympy(beams):
  """
  Use sympy to solve a system of equations for the first three hailstones.
  Given three hailstone positions and vectors, find times t0, t1, and t2
  and starting position and vector for the rock. This totals nine unknown
  values, t0,t1,t2 and 3 dimensions of starting position and vector.

  rock at t0 = hailstone 0 at t0
    pos + t0 vec = pos0 + t0 vec0
  rock at t1 = hailstone 0 at t2
    pos + t1 vec = pos1 + t1 vec1
  rock at t2 = hailstone 0 at t2
    pos + t2 vec = pos2 + t2 vec2

  And since each of those equations will solve for 3 dimensions x,y,z there
  are 9 equations and 9 unknowns.
  """
  rock_pos = sympy.symbols('rp0 rp1 rp2')
  rock_vec = sympy.symbols('rv0 rv1 rv2')
  times = sympy.symbols('t0 t1 t2')

  equations = []
  for hailstone_idx in range(3):
    hail = beams[hailstone_idx]
    t = times[hailstone_idx]
    for dim in range(3):
      eqn = sympy.Eq(sympy.Integer(hail.pos[dim])
                     + t * sympy.Integer(hail.vec[dim]),
                     rock_pos[dim] + t * rock_vec[dim])
      # print(str(eqn))
      equations.append(eqn)

  solns = sympy.solve(equations, rock_pos + rock_vec + times)
  assert len(solns) == 1

  rock_pos = solns[0][:3]
  # print(f'starting pos ({rock_pos[0]}, {rock_pos[1]}, {rock_pos[2]})')
  print(f'part2 {sum(rock_pos)}')
  


if __name__ == '__main__':
  filename = 'day24.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  with open(filename) as inf:
    beams = readInput(inf)
  part1(beams)
  part2sympy(beams)
  
