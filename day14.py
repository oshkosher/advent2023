#!/usr/bin/env python3

"""
Advent of Code 2023, day 14: Parabolic Reflector Dish

Movable items in grid, find cycle.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, copy, time
from common import readGrid, printGrid, gridToString


# enable this to use part2numpy
# In my experiments numpy ended up being around 30x slower,
# perhaps because each time an element is accessed it needs to create a python
# object to encapsulate the value.

# import numpy as np
EMPTY = 0
ROCK = 1
WALL = 255
char_to_int = {'.': EMPTY, '#': WALL, 'O': ROCK}

# invert char_to_int
int_to_char = {b: a for a,b in char_to_int.items()}


def getColumn(grid, c):
  return [grid[r][c] for r in range(len(grid))]


def compileRuns(row, wall = '#'):
  runs = []
  start = 0 if row[0] != wall else None
  for i in range(1, len(row)):
    if row[i] == wall:
      if start != None:
        runs.append((start, i-1))
        start = None
    else:
      if start == None:
        start = i
  if start != None:
    runs.append((start, len(grid)-1))
  return runs
  

def rowRuns(grid):
  return [compileRuns(grid[r]) for r in range(len(grid))]
  

def columnRuns(grid):
  return [compileRuns(getColumn(grid, c)) for c in range(len(grid[0]))]
  

def rowRunsNumpy(grid):
  return [compileRuns(grid[r], WALL) for r in range(grid.shape[0])]


def hashNumpyGrid(grid):
  return hash(grid.tobytes())


def rollNorth(grid):
  some_motion = True

  while some_motion:
    some_motion = False

    for r in range(1, len(grid)):
      for c in range(len(grid[r])):
        if grid[r][c] == 'O' and grid[r-1][c] == '.':
          grid[r-1][c] = 'O'
          grid[r][c] = '.'
          some_motion = True

          
def rollNorthFast(grid, col_runs):
  """
  runs is a 2-d array.
  runs[c] represents column c
  Each entry in runs[c] is a (start,end) tuple noting the
  beginning and end (inclusive) of a range of empty spaces in column[i].
  """
  for c in range(len(grid[0])):
    for start, end in col_runs[c]:
      # ri and wi are like read and write pointers
      # when a stone is found at [ri++], write one at [wi++]
      ri = wi = start

      # move stones to the start of the run
      while ri <= end:
        if grid[ri][c] == 'O':
          grid[wi][c] = 'O';
          wi += 1
        ri += 1

      # empty out the rest of the run
      while wi <= end:
        grid[wi][c] = '.'
        wi += 1
      
          
def rollSouth(grid):
  some_motion = True

  while some_motion:
    some_motion = False

    for r in range(len(grid)-2, -1, -1):
      for c in range(len(grid[r])):
        if grid[r][c] == 'O' and grid[r+1][c] == '.':
          grid[r+1][c] = 'O'
          grid[r][c] = '.'
          some_motion = True

          
def rollSouthFast(grid, col_runs):
  """
  runs is a 2-d array.
  runs[c] represents column c
  Each entry in runs[c] is a (start,end) tuple noting the
  beginning and end (inclusive) of a range of empty spaces in column[i].
  """
  for c in range(len(grid[0])):
    for start, end in col_runs[c]:
      ri = wi = end

      # move stones to the start of the run
      while ri >= start:
        if grid[ri][c] == 'O':
          grid[wi][c] = 'O';
          wi -= 1
        ri -= 1

      # empty out the rest of the run
      while wi >= start:
        grid[wi][c] = '.'
        wi -= 1

          
def rollWest(grid):
  some_motion = True

  while some_motion:
    some_motion = False

    height = len(grid)
    width = len(grid[0])
    for c in range(1, width):
      for r in range(height):
        if grid[r][c] == 'O' and grid[r][c-1] == '.':
          grid[r][c-1] = 'O'
          grid[r][c] = '.'
          some_motion = True

          
def rollRowWestFast(row, row_runs, rock = 'O', empty = '.'):
  for start, end in row_runs:
    ri = wi = start

    # move stones to the start of the run
    while ri <= end:
      if row[ri] == rock:
        row[wi] = rock;
        wi += 1
      ri += 1

    # empty out the rest of the run
    while wi <= end:
      row[wi] = empty
      wi += 1

          
def rollWestFast(grid, row_runs, rock = 'O', empty = '.'):
  for row, row_runs in zip(grid, row_runs):
    rollRowWestFast(row, row_runs, rock, empty)
  
          
def rollWestNumpy(grid, row_runs):
  rollWestFast(grid, row_runs, ROCK, EMPTY)

          
def rollEast(grid):
  some_motion = True

  while some_motion:
    some_motion = False

    height = len(grid)
    width = len(grid[0])
    for c in range(width-2, -1, -1):
      for r in range(height):
        if grid[r][c] == 'O' and grid[r][c+1] == '.':
          grid[r][c+1] = 'O'
          grid[r][c] = '.'
          some_motion = True

          
def rollRowEastFast(row, row_runs, rock = 'O', empty = '.'):
  for start, end in row_runs:
    ri = wi = end

    # move stones to the start of the run
    while ri >= start:
      if row[ri] == rock:
        row[wi] = rock;
        wi -= 1
      ri -= 1

    # empty out the rest of the run
    while wi >= start:
      row[wi] = empty
      wi -= 1


def rollEastFast(grid, row_runs, rock = 'O', empty = '.'):
  for row, row_runs in zip(grid, row_runs):
    rollRowEastFast(row, row_runs, rock, empty)
  
          
def rollEastNumpy(grid, row_runs):
  rollEastFast(grid, row_runs, ROCK, EMPTY)


def rollNorthNumpy(grid_t, col_runs):
  rollWestNumpy(grid_t, col_runs)


def rollSouthNumpy(grid_t, col_runs):
  rollEastNumpy(grid_t, col_runs)


def spin(grid, count):
  for _ in range(count):
    rollNorth(grid)
    rollWest(grid)
    rollSouth(grid)
    rollEast(grid)


def spinFast(grid, count, row_runs, column_runs):
  for _ in range(count):
    rollNorthFast(grid, column_runs)
    rollWestFast(grid, row_runs)
    rollSouthFast(grid, column_runs)
    rollEastFast(grid, row_runs)


def spinNumpy(grid, grid_t, count, row_runs, column_runs):
  for _ in range(count):
    rollNorthNumpy(grid_t, column_runs)
    rollWestNumpy(grid, row_runs)
    rollSouthNumpy(grid_t, column_runs)
    rollEastNumpy(grid, row_runs)
    

def roundRockCount(row):
  i = 0
  for r in row:
    if r == 'O':
      i += 1

  return i


def hashGrid(grid):
  return hash(gridToString(grid))


def northLoad(grid):
  load = 0
  moment = len(grid)
  for row in grid:
    load += moment * roundRockCount(row)
    moment -= 1
  return load


def part1(grid):
  rollNorth(grid)
  print(f'part1 {northLoad(grid)}')


def part2(grid):
  row_runs = rowRuns(grid)
  column_runs = columnRuns(grid)
  
  goal_count = 10**9

  success = False
  cycle_length = None
  spin_count = 0
  hashes = {}
  # print(f'spins={spin_count}, north load = {northLoad(grid)}, hash={hashGrid(grid)}')
  # printGrid(grid)
  while spin_count <= 10000:
    # spin(grid, 1);
    spinFast(grid, 1, row_runs, column_runs);
    grid_hash = hashGrid(grid)
    spin_count += 1
    # print(f'spins={spin_count}, north load = {northLoad(grid)}, hash={grid_hash}')
    sys.stdout.write(f'\rspin {spin_count}')
    if grid_hash in hashes:
      print(f'\nCycle found at spin counts {hashes[grid_hash]}, {spin_count}')
      cycle_length = spin_count - hashes[grid_hash]
      success = True
      break
    hashes[grid_hash] = spin_count
    
  if not success:
    print('No cycle found.')
    return 1
    
  # printGrid(grid)
  # print(f'North load = {northLoad(grid)}')

  assert cycle_length != None

  # say the cycle length is 10 and we're at spin_count 13.
  # it'll take 7 more spins until we match what we'll be at 100

  additional_spins = (goal_count - spin_count) % cycle_length
  # spin(grid, additional_spins)
  spinFast(grid, additional_spins, row_runs, column_runs)
  
  spin_count += additional_spins

  # print(f'North load at {spin_count} and {goal_count} = {northLoad(grid)}, hash={hashGrid(grid)}')
  print(f'part2 {northLoad(grid)}')


def numpyRowToString(row):
  return ''.join([int_to_char[x] for x in row])


def printNumpyGrid(grid):
  for row in grid:
    print(numpyRowToString(row))


def numpyGridToString(grid):
  return '\n'.join([numpyRowToString(row) for row in grid])


def part2numpy(grid_orig):
  height = len(grid_orig)
  width = len(grid_orig[0])
  grid = np.zeros((height, width)).astype(np.intc)
  char_to_int = {'.': 0, '#': WALL, 'O': 1}
  for r, row in enumerate(grid_orig):
    for c, cell in enumerate(row):
      grid[r][c] = char_to_int[cell]

  # this makes a view of the grid, not a copy
  grid_t = grid.transpose()
  # grid_mirror_row = numpy.flip(grid, 1)
  # grid_mirror_col = numpy.flip(grid, 0)

  # printNumpyGrid(grid)

  row_runs = rowRunsNumpy(grid)
  column_runs = rowRunsNumpy(grid_t)

  spin_count = 10
  
  print('orig')
  # rollSouth(grid_orig)
  # rollSouthFast(grid_orig, column_runs)
  # spin(grid_orig, 10)
  timer_old = time.time()
  spinFast(grid_orig, spin_count, row_runs, column_runs)
  timer_old = time.time() - timer_old
  orig_str = gridToString(grid_orig)
  print(orig_str)

  print('\nnumpy')
  timer_numpy = time.time()
  spinNumpy(grid, grid_t, spin_count, row_runs, column_runs)
  timer_numpy = time.time() - timer_numpy
  # rollSouthNumpy(grid_t, column_runs)
  numpy_str = numpyGridToString(grid)
  print(numpy_str)
  if orig_str != numpy_str:
    print("ERROR mismatch")

  print(f'orig {timer_old}, numpy {timer_numpy}')


if __name__ == '__main__':
  filename = 'day14.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  grid = readGrid(filename, True)
  part1(copy.deepcopy(grid))
  part2(copy.deepcopy(grid))
  # part2numpy(grid)
