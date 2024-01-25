#!/usr/bin/env python3

"""
Advent of Code 2023, day 11: Hot Springs

Processing run-length compressed data without expanding it.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, copy
from common import readGrid

def isEmptyColumn(grid, c):
  for r in grid:
    if r[c] != '.': return False
  return True

def insertEmptyColumn(grid, c):
  #print(f'empty col {c}')
  for r in grid:
    r[c:c] = ['.']

def isEmptyRow(grid, r):
  for e in grid[r]:
    if e != '.': return False
  return True

def insertEmptyRow(grid, r):
  grid[r:r] = [['.' for _ in range(len(grid[r]))]]

def expandUniverse(grid):
  for r in range(len(grid)-1, -1, -1):
    if isEmptyRow(grid, r):
      insertEmptyRow(grid, r)
  for c in range(len(grid[0])-1, -1, -1):
    if isEmptyColumn(grid, c):
      insertEmptyColumn(grid, c)
  

def listGalaxies(grid):
  galaxies = []
  for r, row in enumerate(grid):
    for c, e in enumerate(row):
      if e == '#':
        galaxies.append((r,c))
  return galaxies


def printGrid(grid):
  for row in grid:
    if isinstance(row, list):
      print(''.join([str(e) for e in row]))
    else:
      print(row)


def part1(grid):
  expandUniverse(grid)
  galaxies = listGalaxies(grid)
  # printGrid(grid)
  # for g in galaxies:
  #   print(f'({g[0]}, {g[1]})')
  dist_sum = 0
  for g1 in range(len(galaxies) - 1):
    for g2 in range(g1+1, len(galaxies)):
      d = abs(galaxies[g1][0] - galaxies[g2][0]) + abs(galaxies[g1][1] - galaxies[g2][1])
      dist_sum += d
      # print(f'{g1}-{g2}  {d}')
  print(f'part1 {dist_sum}')


def part2(grid):
  o = 0
  col_offsets = [0] * len(grid[0])
  for c in range(len(grid[0])):
    if isEmptyColumn(grid, c):
      o += 999999
    col_offsets[c] = o
    
  o = 0
  row_offsets = [0] * len(grid)
  for r in range(len(grid)):
    if isEmptyRow(grid, r):
      o += 999999
    row_offsets[r] = o
    
  # expandUniverse(grid)
  # print(f'cols {col_offsets}')
  # print(f'rows {row_offsets}')
  galaxies = listGalaxies(grid)
  for i in range(len(galaxies)):
    g = galaxies[i]
    galaxies[i] = (g[0] + row_offsets[g[0]], g[1] + col_offsets[g[1]])
  
  # printGrid(grid)
  # for g in galaxies:
  #   print(f'({g[0]}, {g[1]})')
  dist_sum = 0
  for g1 in range(len(galaxies) - 1):
    for g2 in range(g1+1, len(galaxies)):
      d = abs(galaxies[g1][0] - galaxies[g2][0]) + abs(galaxies[g1][1] - galaxies[g2][1])
      dist_sum += d
      # print(f'{g1}-{g2}  {d}')
  print(f'part2 {dist_sum}')


if __name__ == '__main__':
  filename = 'day11.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  with open(filename) as inf:
    grid = readGrid(inf, True)
  part1(copy.deepcopy(grid))
  part2(grid)
