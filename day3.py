#!/usr/bin/env python3

"""
Advent of Code 2023, day 3: Gear Ratios

Adjacency logic in 2-d grid.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, re
from common import readGrid

num_re = re.compile(r'\d+')


class Stars:

  def __init__(self):
    # (row,col) -> [list of number values]
    self.stars = {}

  def add(self, value, star_row, star_col):
    key = (star_row, star_col)
    if key not in self.stars:
      self.stars[key] = []
    self.stars[key].append(value)

  def sumGears(self):
    sum = 0
    for (key, value_list) in self.stars.items():
      if len(value_list) == 2:
        # print(f'star at {key[0]},{key[1]}: {value_list[0]}*{value_list[1]}')
        sum += value_list[0] * value_list[1]
    return sum


def isInRange(grid, row, col):
  return (0 <= row < len(grid)) and (0 <= col < len(grid[0]))


def isSymbol(grid, row, col):
  if not isInRange(grid, row, col): return False
  c = grid[row][col]
  return c != '.' and not c.isdigit()


def isStar(grid, row, col):
  return isInRange(grid, row, col) and grid[row][col] == '*'
  

def hasAdjacentSymbol(grid, row, start, end):
  for col in range(start-1, end+1):
    # above
    if isSymbol(grid, row-1, col): return True
    # below
    if isSymbol(grid, row+1, col): return True

  # left
  if isSymbol(grid, row, start-1): return True
  
  # right
  if isSymbol(grid, row, end): return True

  return False
  

def addToAdjacentStars(value, stars, grid, row, start, end):
  for col in range(start-1, end+1):
    # above
    if isStar(grid, row-1, col): stars.add(value, row-1, col)
    # below
    if isStar(grid, row+1, col): stars.add(value, row+1, col)

  # left
  if isStar(grid, row, start-1): stars.add(value, row, start-1)
  
  # right
  if isStar(grid, row, end): stars.add(value, row, end)

  return False
    
  
def part1(filename):
  grid = readGrid(filename)
  sum = 0
  for r in range(len(grid)):
    # print(f'row {r}')
    for num_match in re.finditer(num_re, grid[r]):
      # print(f'"{num_match.group(0)}" at {num_match.start(0)}..{num_match.end(0)}')
      num = int(num_match.group(0))
      if hasAdjacentSymbol(grid, r, num_match.start(0), num_match.end(0)):
        # print(f'has adjacent: {num}')
        sum += num

  print(f'part1 {sum}')


def part2(filename):
  grid = readGrid(filename)
  sum = 0
  stars = Stars()
  for r in range(len(grid)):
    # print(f'row {r}')
    for num_match in re.finditer(num_re, grid[r]):
      # print(f'"{num_match.group(0)}" at {num_match.start(0)}..{num_match.end(0)}')
      num = int(num_match.group(0))
      # print(f'{num} at row {r}, cols {num_match.start(0)}-{num_match.end(0)}')
      addToAdjacentStars(num, stars, grid, r,
                         num_match.start(0), num_match.end(0))


  print(f'part2 {stars.sumGears()}')
  

if __name__ == '__main__':
  filename = 'day3.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
