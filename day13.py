#!/usr/bin/env python3

"""
Advent of Code 2023, day 13: Point of Incidence

Reflections, one bit differences.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys

def readGrids(inf):
  grid = []
  while True:
    line = inf.readline()
    if not line:
      if grid:
        yield grid
      break
    elif line == '\n':
      yield grid
      grid = []
    else:
      grid.append(line.strip())


def printGrid(grid):
  for row in grid:
    if isinstance(row, list):
      print(''.join([str(e) for e in row]))
    else:
      print(row)


def colHash(grid, c):
  col = ''.join([row[c] for row in grid])
  # print(f'col {c} {repr(col)} {hash(col)}')
  return hash(col)

def colHashes(grid):
  return [colHash(grid, c) for c in range(len(grid[0]))]

def colBits(grid, c):
  s = 0
  b=1
  for row in grid[::-1]:
    if row[c] == '#':
      s += b
    b *= 2
  return s

def colBitses(grid):
  return [colBits(grid, c) for c in range(len(grid[0]))]

def rowHash(grid, r):
  return hash(grid[r])

def rowHashes(grid):
  return [rowHash(grid, r) for r in range(len(grid))]

def rowBits(grid, r):
  s = 0
  b=1
  for x in grid[r][::-1]:
    if x == '#':
      s += b
    b *= 2
  return s

def rowBitses(grid):
  return [rowBits(grid, r) for r in range(len(grid))]

def isReflection(a, m):
  # returns True if a[0:m] == a[m:] reversed
  # 0 1 2 3 4 5
  #       m
  #    m-1
  #  m-2   m+1
  lo = m-1
  hi = m
  while lo >= 0 and hi < len(a):
    if a[lo] != a[hi]: return False
    lo -= 1
    hi += 1
  return True

def isAlmostReflection(a, m):
  lo = m-1
  hi = m
  almost_found = False
  while lo >= 0 and hi < len(a):
    if a[lo] != a[hi]:
      if isSimilar(a[lo], a[hi]):
        if not almost_found:
          almost_found = True
        else:
          return False
      else:
        return False
    lo -= 1
    hi += 1
  return almost_found

def isSimilar(a, b):
  # returns true iff a and b differ in exactly one bit
  x = a ^ b
  if x == 0: return False
  return (x & (x-1)) == 0

def findReflection(a):
  for m in range(1, len(a)):
    if isReflection(a, m):
      return m
  return None

def findAlmostReflection(a):
  for m in range(1, len(a)):
    if isAlmostReflection(a, m):
      return m
  return None


def part1(filename):
  with open(filename) as inf:
    sum = 0
    for grid in readGrids(inf):
      # printGrid(grid)
      # rh = rowHashes(grid)
      rh = rowBitses(grid)
      m = findReflection(rh)
      if m != None:
        # print(f'{m} rows')
        sum += 100 * m
        continue

      # ch = colHashes(grid)
      ch = colBitses(grid)
      m = findReflection(ch)
      if m != None:
        # print(f'{m} cols')
        sum += m
        continue

      print('Noone!')

      # print(repr(ch))
      # print(repr(rh))
      # print()

  print(f'part1 {sum}')
  # 37561


def part2(filename):
  with open(filename) as inf:
    sum = 0
    for grid in readGrids(inf):
      # printGrid(grid)
      # print()
      row_bits = rowBitses(grid)
      # for r1 in range(len(row_bits)):
      #   for r2 in range(r1+1, len(row_bits)):
      #     if isSimilar(row_bits[r1], row_bits[r2]):
      #       print(f'  similar rows {r1}, {r2}')

      m = findAlmostReflection(row_bits)
      if m != None:
        # print(f'{m} rows')
        sum += 100 * m
        continue

      col_bits = colBitses(grid)
      # for c1 in range(len(col_bits)):
      #   for c2 in range(c1+1, len(col_bits)):
      #     if isSimilar(col_bits[c1], col_bits[c2]):
      #       print(f'  similar cols {c1}, {c2}')

      m = findAlmostReflection(col_bits)
      if m != None:
        # print(f'{m} cols')
        sum += m
        # continue
          
  print(f'part2 {sum}')


if __name__ == '__main__':
  filename = 'day13.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)

