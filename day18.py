#!/usr/bin/env python3

"""
Advent of Code 2023, day 18: Lavaduct Lagoon

Find interior area given the boundary.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, re
from collections import deque

line_re = re.compile(r'([UDLR]) (\d+) \(#([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])([0-9a-f][0-9a-f])\)')
line2_re = re.compile(r'[UDLR] \d+ \(#([0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f])([0-9a-f])\)')


def readInput(filename):
  """
  Return list of (direction, count, R, G, B) tuples
  """
  with open(filename) as inf:
    steps = []
    for line in inf:
      m = line_re.search(line)
      if not m:
        print(f'Bad input line: {line!r}')
        continue
      steps.append((charToDir[m.group(1)], int(m.group(2)), int(m.group(3),16), int(m.group(4),16), int(m.group(5),16)))
  return steps


def readInput2(filename):
  """
  Return list of (direction, count) tuples
  """
  with open(filename) as inf:
    steps = []
    for line in inf:
      m = line2_re.search(line)
      if not m:
        print(f'Bad input line: {line!r}')
        continue
      d = 2+int(m.group(2))
      if d == 5: d = 1
      count = int(m.group(1), 16)
      steps.append((d, count))
  return steps


UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4
      
dirStr = {UP: 'UP',
          RIGHT: 'RIGHT',
          DOWN: 'DOWN',
          LEFT: 'LEFT'}

charToDir = {'U': UP,
             'R': RIGHT,
             'D': DOWN,
             'L': LEFT}

def move(r, c, d, count=1):
  if d == UP:
    return (r-count,c)
  elif d == RIGHT:
    return (r,c+count)
  elif d == DOWN:
    return (r+count,c)
  else:
    return (r,c-count)

def invDir(d):
  d += 2
  if d > 4: d -= 4
  return d

def rightTurn(d):
  if d == LEFT:
    return UP
  else:
    return d + 1

def leftTurn(d):
  if d == UP:
    return LEFT
  else:
    return d - 1

def turnAngle(p, d):
  # previous_direction, new_direction
  if p == d: return 0
  elif d == rightTurn(p): return 90
  elif d == leftTurn(p): return -90
  else: return 180


  

"""
 XXX
XX X
X  X
XXXX
  XX

4*5 - 1 - 2 = 17

"""


def trace(steps):
  # step: (direction, count, R, G, B) tuples
  r = c = 0

  min_r = max_r = min_c = max_c = 0

  pd = steps[-1][0]   # previous direction
  turns = 0
  reversals = 0

  for i, step in enumerate(steps):
    d = step[0]
    count = step[1]
    t = turnAngle(pd, d)
    if t == 180: reversals += 1
    turns += t
    r,c = move(r, c, d, count)
    min_r = min(min_r, r)
    min_c = min(min_c, c)
    max_r = max(max_r, r)
    max_c = max(max_c, c)
    pd = d
    # print(f'step {i} turn {t}, {dirStr[d]} {count}, ({r},{c})')

  # print(f'after {len(steps)} pos=({r},{c}), turns={turns}, {reversals} reversals')
  # print(f'rows {min_r}..{max_r}, cols {min_c}..{max_c}')

  return min_r, min_c, max_r, max_c


def initGrid(min_r, min_c, max_r, max_c):
  # return (grid, start_row, start_col)
  height = max_r - min_r + 1
  width = max_c - min_c + 1
  grid = [['.'] * width for _ in range(height)]
  # grid[-min_r][-min_c] = 'S'
  return (grid, -min_r, -min_c)


def printGrid(grid):
  for row in grid:
    if isinstance(row, list):
      print(''.join([str(e) for e in row]))
    else:
      print(row)


def draw(grid, start_row, start_col, steps):
  r = start_row
  c = start_col

  # grid[r][c] = 'S'
  for step in steps:
    d, n = step[0:2]
    for i in range(n):
      r,c = move(r, c, d)
      grid[r][c] = '#'

  # grid[r][c] = 'E'
  # printGrid(grid)


cw_inside_offset = {
  UP: (0,1),
  RIGHT: (1,0),
  DOWN: (0,-1),
  LEFT: (-1,0),
  }


def qIfEmpty(r, c, grid, fillq):
  if grid[r][c] == '.':
    grid[r][c] = '#'
    fillq.append((r,c))


def fill(fillq, grid):
  while fillq:
    r,c = fillq.pop()
    if r>0:
      qIfEmpty(r-1, c, grid, fillq)
    if c>0:
      qIfEmpty(r, c-1, grid, fillq)
    if r<len(grid)-1:
      qIfEmpty(r+1, c, grid, fillq)
    if c<len(grid[0])-1:
      qIfEmpty(r, c+1, grid, fillq)
    # printGrid(grid)
    # print(len(fillq))
  

def traceFill(grid, start_row, start_col, steps):
  # right turns, clockwise
  r = start_row
  c = start_col

  fillq = deque()

  # grid[r][c] = 'S'
  for step in steps:
    d, n = step[0:2]
    o = cw_inside_offset[d]
    qIfEmpty(r+o[0], c+o[1], grid, fillq)
    fill(fillq, grid)
    for _ in range(n):
      r,c = move(r, c, d)
      qIfEmpty(r+o[0], c+o[1], grid, fillq)
      fill(fillq, grid)


def countFilled(grid):
  n = 0
  for row in grid:
    for c in row:
      if c != '.':
        n += 1
  return n


def part1(filename):
  steps = readInput(filename)
  min_r, min_c, max_r, max_c = trace(steps)
  (grid, start_row, start_col) = initGrid(min_r, min_c, max_r, max_c)
  draw(grid, start_row, start_col, steps)
  count_outline = countFilled(grid)
  traceFill(grid, start_row, start_col, steps)
  count_filled = countFilled(grid)
  print(f'part1 {count_filled}')
  # count_filled = greenTheoremPerimeter(steps)
  # print(f'green thm {count_filled}')


def greenTheoremPerimeter(steps):
  """
  up, when traversing clockwise, signifies area removed from the total.
  down signifies addition.
  variations:

    ###   if up, -(n+1)
    #     down, +(n-1)
    #
    ###

    ###   if up, -n
    #     down, +n
    #
  ###

  ###     if up, -n
    #     down, +n
    #
    ###

  ###     if up, -(n-1)
    #     down, +(n+1)
    #
  ###
  """

  step_count = len(steps)
  # temporarily duplicate the first move at the end to make boundary check easier
  steps.append(steps[0])

  area = c = 0
  
  # steps always make 90 degree turns, so it's always
  # left|right followed by up|down.
  # if the first step is left|right, process it now so the first step
  # processed by the loop is up|down
  si = 0
  if steps[si][0] in {LEFT, RIGHT}:
    if steps[si][0] == LEFT:
      c -= steps[si][1]
    else:
      c += steps[si][1]
    si += 1
  
  while si < step_count:
    s = steps[si]
    dp = steps[si-1][0]  # previous direction, left|right
    d = s[0]     # current direction, up|down
    dn = steps[si+1][0]  # next direction, left|right
    n = s[1]     # length of this step

    assert d in {UP, DOWN}
    assert dp in {LEFT, RIGHT}
    assert dn in {LEFT, RIGHT}

    if dp == dn:
      count = n
    else:
      if dp == LEFT:
        if d == UP:  # left, up, right
          count = n+1
        else:
          count = n-1
      else:
        if d == UP:  # right, up, left
          count = n-1
        else:
          count = n+1

    if d == UP:
      sign = -1
      thickness = 0
    else:
      sign = 1
      thickness = 1

    area += sign * count * (c + thickness)
    # print(f'{dirStr[d]} {n} at {c}, area{sign*count:+}*{c+thickness}={area}')
    
    si += 1
    s = steps[si]
    d = s[0]     # current direction, left|right
    n = s[1]     # length of this step

    assert d in {LEFT, RIGHT}

    if d == LEFT:
      c -= n
    else:
      c += n

    si += 1

  return area


def part2(filename):
  steps = readInput2(filename)

  count_filled = greenTheoremPerimeter(steps)
  print(f'part2 {count_filled}')


if __name__ == '__main__':
  filename = 'day18.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
