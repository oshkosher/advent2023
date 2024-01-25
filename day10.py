#!/usr/bin/env python3

"""
Advent of Code 2023, day 10: Pipe Maze

Tracing boundaries to find enclosed area

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys
from common import *

dirStr = {UP: 'UP',
          RIGHT: 'RIGHT',
          DOWN: 'DOWN',
          LEFT: 'LEFT'}

pipes = {
  '|': (UP,DOWN),
  '-': (RIGHT,LEFT),
  'L': (UP,RIGHT),
  'J': (UP,LEFT),
  '7': (DOWN,LEFT),
  'F': (RIGHT,DOWN),
  }

pipe_inv = {}
# (pipe,in_dir): out_dir
goes = {}
for k,v in pipes.items():
  pipe_inv[v] = k
  goes[(k,v[0])] = v[1]
  goes[(k,v[1])] = v[0]

def findStart(grid):
  for r, row in enumerate(grid):
    for c, e in enumerate(row):
      if e == 'S':
        return (r,c)
  raise 'hey, no S'

def startPipe(grid, start_pos):
  r,c = start_pos
  dirs = []
  if (grid[r-1][c], DOWN) in goes:
    dirs.append(UP)
  if (grid[r][c+1], LEFT) in goes:
    dirs.append(RIGHT)
  if (grid[r+1][c], UP) in goes:
    dirs.append(DOWN)
  if (grid[r][c-1], RIGHT) in goes:
    dirs.append(LEFT)

  return pipe_inv[tuple(dirs)]

def loopLength(grid, start_pos, start_pipe):
  r,c = start_pos
  

def part1(grid):
  (r,c) = start_pos = findStart(grid)
  start_pipe = startPipe(grid, start_pos)

  d = pipes[start_pipe][0]
  (r,c) = move(r,c,d)
  # d = invDir(d)
  # print(f'({r},{c}) {dirStr[d]}')
  
  dist = 1
  while (r,c) != start_pos:
    p = grid[r][c]
    d = goes[(p,invDir(d))]
    # print(dirStr[d])
    (r,c) = move(r,c,d)
    dist += 1
    
  print(f'part1 {dist//2}')


# state transitions when determining enclosed regions
# direction is always left-to-right
# (side,pipe) -> (side, cross)
# if cross is 1, then passing this cell inverts our inside/outside status
# side = LEFT, UP, or DOWN
def isCrossing(side, pipe):
  if pipe =='.':
    return (LEFT, 0)
  elif pipe == '|':
    return (LEFT, 1)
  elif pipe =='-':
    return (side, 0)
  elif pipe =='L':
    return (DOWN, 0)
  elif pipe =='J':
    if side == UP:
      return (LEFT, 1)
    elif side == DOWN:
      return (LEFT, 0)
    else:
      raise 'prob'
    return (LEFT, 1)
  elif pipe =='7':
    if side == UP:
      return (LEFT, 0)
    elif side == DOWN:
      return (LEFT, 1)
    else:
      raise 'prob'
    return (LEFT, 1)
  elif pipe =='F':
    return (UP, 0)
  else:
    raise 'prob'
  

def part2(grid):
  (r,c) = start_pos = findStart(grid)
  start_pipe = startPipe(grid, start_pos)

  d = pipes[start_pipe][0]
  (r,c) = move(r,c,d)
  # d = invDir(d)
  # print(f'({r},{c}) {dirStr[d]}')

  fill = [['.' for _ in row] for row in grid]
  fill[r][c] = grid[r][c]
  
  while (r,c) != start_pos:
    p = grid[r][c]
    d = goes[(p,invDir(d))]
    # print(dirStr[d])
    (r,c) = move(r,c,d)
    fill[r][c] = grid[r][c]
    
  # printGrid(fill)

  count = 0
  inside = 0
  side = DOWN
  inflag = {0: 'O', 1: 'i'}
  for r, row in enumerate(grid):
    for c, p in enumerate(row):
      if p == 'S':
        p = start_pipe
      if fill[r][c] == '.':
        fill[r][c] = inflag[inside]
        count += inside
      else:
        (side, cross) = isCrossing(side, p)
        if cross:
          inside = 1 - inside
  # print()
  # printGrid(fill)
  print(f'part2 {count}')


if __name__ == '__main__':
  filename = 'day10.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]

  with open(filename) as inf:
    grid = readGrid(inf)
  part1(grid)
  part2(grid)
