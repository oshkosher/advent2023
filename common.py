#!/usr/bin/env python3

"""
Common code for Advent of Code puzzles.
"""

UP = NORTH = 1
RIGHT = EAST = 2
DOWN = SOUTH = 3
LEFT = WEST = 4

heading_names = (None, 'NORTH', 'EAST', 'SOUTH', 'WEST')
direction_names = (None, 'UP', 'RIGHT', 'DOWN', 'LEFT')

def readGrid(inf, split_rows_into_lists = False):
  """
  Read a 2-d grid.
  inf can be either a filename or input stream.
  If split_rows_into_lists is True, the return a list of list of characters.
  Otherwise, return a list of strings.

  A list of a list of characters is useful if the cells will be modified, because
  string are immutable.
  """
  filename = None
  if isinstance(inf, str):
    filename = inf
    inf = open(filename)
    
  rows = []
  while True:
    line = inf.readline().rstrip()
    if line == '': break
    if split_rows_into_lists:
      line = [c for c in line]
    rows.append(line)

  if filename:
    inf.close()
    
  return rows


def createGrid(row_count, col_count, split_rows_into_lists=False, fill='.'):
  if split_rows_into_lists:
    return [[fill]*col_count for _ in range(row_count)]
  else:
    return [fill*col_count for _ in range(row_count)]


def gridGet(grid, coord):
  return grid[coord[0]][coord[1]]


def pasteGrid(dest_grid, dest_row, dest_col, src_grid):
  src_width = len(src_grid[0])
  if type(dest_grid[0]) == list:
    if type(src_grid[0]) == list:
      for r, src_row in enumerate(src_grid):
        dest_grid[dest_row+r][dest_col:dest_col+src_width] = src_row
    else:
      for r, src_row in enumerate(src_grid):
        dest_grid[dest_row+r][dest_col:dest_col+src_width] = [x for x in src_row]
  else:
    if type(src_grid[0]) == str:
      for r, src_row in enumerate(src_grid):
        tmp = dest_grid[dest_row+r]
        dest_grid[dest_row+r] = tmp[:dest_col] + src_row + tmp[dest_col+src_width:]
    else:
      for r, src_row in enumerate(src_grid):
        tmp = dest_grid[dest_row+r]
        dest_grid[dest_row+r] = tmp[:dest_col] + ''.join(src_row) + tmp[dest_col+src_width:]


def gridRowToString(row):
  if isinstance(row, list):
    return ''.join([str(e) for e in row])
  else:
    return row
      

def printGrid(grid):
  for row in grid:
    print(gridRowToString(row))

    
def gridToString(grid):
  return '\n'.join([gridRowToString(row) for row in grid])
  


def gridSearch(grid, target):
  for r, row in enumerate(grid):
    for c, e in enumerate(row):
      if e == target:
        return (r, c)
  return False


def gridCount(grid, target):
  n = 0
  for row in grid:
    for e in row:
      if e == target:
        n += 1
  return n


def deepCopyGrid(grid):
  return [r.copy() for r in grid]


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


def testPasteGrid():
  src = createGrid(3, 5, True, 'o')
  dest = createGrid(10, 10, False, '.')
  pasteGrid(dest, 1, 2, src)
  printGrid(dest)

  
def list2str(lst):
  return ' '.join([str(x) for x in lst])


if __name__ == '__main__':
  testPasteGrid()
