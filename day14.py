#!/usr/bin/env python3

"""
Advent of Code 2023, day 14: Parabolic Reflector Dish

Movable items in grid, find cycle.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, copy
from common import readGrid


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


def spin(grid, count):
  for _ in range(count):
    rollNorth(grid)
    rollWest(grid)
    rollSouth(grid)
    rollEast(grid)

def roundRockCount(row):
  i = 0
  for r in row:
    if r == 'O':
      i += 1

  return i


def hashGrid(grid):
  s = ''.join([''.join(row) for row in grid])
  return hash(s)


def northLoad(grid):
  load = 0
  moment = len(grid)
  for row in grid:
    load += moment * roundRockCount(row)
    moment -= 1
  return load

def printGrid(grid):
  for row in grid:
    print(''.join(row))


def part1(grid):
  rollNorth(grid)
  print(f'part1 {northLoad(grid)}')


def part2(grid):
  # grid_orig = copy.deepcopy(grid)

  goal_count = 10**9

  success = False
  cycle_length = None
  spin_count = 0
  hashes = {}
  # print(f'spins={spin_count}, north load = {northLoad(grid)}, hash={hashGrid(grid)}')
  # printGrid(grid)
  while spin_count <= 10000:
    spin(grid, 1);
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
  spin(grid, additional_spins)
  spin_count += additional_spins

  # print(f'North load at {spin_count} and {goal_count} = {northLoad(grid)}, hash={hashGrid(grid)}')
  print(f'part2 {northLoad(grid)}')



if __name__ == '__main__':
  filename = 'day14.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  grid = readGrid(filename, True)
  part1(copy.deepcopy(grid))
  part2(grid)

