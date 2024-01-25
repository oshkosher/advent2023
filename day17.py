#!/usr/bin/env python3

"""
Advent of Code 2023, day 17: Clumsy Crucible

Use Dijkstra's algorithm to find optimal path, but with
special restrictions.

Ed Karrels, ed.karrels@gmail.com, January 2023
"""

import sys, random
import eheap
from common import *

INF = 2**60


AXIS_VERT = 0
AXIS_HORIZ = 1


def dirAxis(d):
  return [None, AXIS_VERT, AXIS_HORIZ, AXIS_VERT, AXIS_HORIZ][d]


def axisName(axis):
  return 'horiz' if axis else 'vert'


def dirString(d):
  return ['', 'up', 'right', 'down', 'left'][d]


def dirChar(d):
  return ['o', '^', '>', 'v', '<'][d]


def bestStr(best):
  return 'inf' if best == INF else str(best)


class Node:
  def __init__(self, row, col, cost, entry_axis):
    self.row = row
    self.col = col
    self.cost = cost  # cost to enter this node
    self.entry_axis = entry_axis  # AXIS_HORIZ or AXIS_VERT
    
    # cost to get here on best-known path
    self.best = INF

    # previous node
    self.prev = None

    self.entry_direction = None
    self.entry_run = None

    self.is_optimal = False

  def reset(self):
    self.best = INF
    self.prev = None
    self.is_optimal = False
    
    
  def __repr__(self):
    pr = self.prev.row
    pc = self.prev.col
    return f'Node({self.row},{self.col} {axisName(self.entry_axis)} ' \
      f'cost={self.cost} best={bestStr(self.best)} prev={pr},{pc} ' \
      f'opt={self.is_optimal})'

  def __lt__(self, other):
    return self.best < other.best


def readInput(filename):
  """
  Return 2-d grid, where each cell is a 2-element list consisting
  of a vertical node and a horizontal node.
  grid[row][col][AXIS_VERT] is a Node
  grid[row][col][AXIS_VERT].entry_axis == AXIS_VERT
  grid[row][col][AXIS_HORIZ].entry_axis == AXIS_HORIZ
  """
  
  def lineToNodes(line, r):
    line = line.strip()
    for c, digit in enumerate(line):
      cost = int(digit)
      n1 = Node(r, c, cost, AXIS_VERT)
      n2 = Node(r, c, cost, AXIS_HORIZ)
      yield (n1,n2)
      
  grid = []
  r = -1   # row index

  with open(filename) as inf:
    for line in inf:
      r += 1
      grid.append(list(lineToNodes(line, r)))

  return grid


def printableBest(cell):
  v,h = cell
  vopt = '*' if v.is_optimal else ''
  hopt = '*' if h.is_optimal else ''
  vbest = str(v.best) if v.best < INF else ''
  hbest = str(h.best) if h.best < INF else ''
  ventry = 'v' if v.entry_direction == DOWN else '^' if v.entry_direction == UP else '|'
  hentry = '>' if h.entry_direction == RIGHT else '<' if h.entry_direction == LEFT else '-'
  return f'{v.cost}{ventry}{vopt}{vbest}{hentry}{hopt}{hbest}'.ljust(10)


def printBests(grid):
  """
  2>*102
  """
  for r, row in enumerate(grid):
    line = f'{r:3} ' + ' '.join([printableBest(e) for e in row])
    print(line)


def reportHeap(h):
  values = []
  for i in range(len(h)):
    v = h.get(i).best
    if v != INF: values.append(v)
  values = [str(v) for v in values]
  # print(f'heap size={len(h)}: {values}')

  
def dijkstra(grid, min_run, max_run):
  # initialize all nodes best=INF, prev=None, is_optimal=False

  height = len(grid)
  width = len(grid[0])

  grid[0][0][AXIS_VERT].best = 0
  grid[0][0][AXIS_VERT].is_optimal = True
  grid[0][0][AXIS_HORIZ].best = 0
  grid[0][0][AXIS_HORIZ].is_optimal = True
  
  node_heap = []
  for row in grid:
    for cell in row:
      node_heap.append(cell[AXIS_VERT])
      node_heap.append(cell[AXIS_HORIZ])

  node_heap = eheap.Heap(node_heap)

  while len(node_heap) > 0:
    # sys.stdout.write(f'\rheap size {len(node_heap)}')
    # printBests(grid)
    # reportHeap(node_heap)
    node = node_heap.pop()
    r = node.row
    c = node.col
    node.is_optimal = True

    depart_axis = 1 - node.entry_axis

    if node.entry_axis == AXIS_VERT:
      # entered vertically, must exit horizontally

      # RIGHT
      cost = 0
      for run in range(1, max_run+1):
        if c + run >= width: break
        cost += grid[r][c+run][0].cost
        if run >= min_run:
          relax(grid, node_heap, node, RIGHT, run, cost)

      # LEFT
      cost = 0
      for run in range(1, max_run+1):
        if c - run < 0: break
        cost += grid[r][c-run][0].cost
        if run >= min_run:
          relax(grid, node_heap, node, LEFT, run, cost)
      
    else:
      # entered horizontally, must exit vertically

      # UP
      cost = 0
      for run in range(1, max_run+1):
        if r - run < 0: break
        cost += grid[r-run][c][0].cost
        if run >= min_run:
          relax(grid, node_heap, node, UP, run, cost)

      # DOWN
      cost = 0
      for run in range(1, max_run+1):
        if r + run >= height: break;
        cost += grid[r+run][c][0].cost
        if run >= min_run:
          relax(grid, node_heap, node, DOWN, run, cost)

  # print()


def relax(grid, node_heap, prev, direction, dist, extra_cost):
  r,c = move(prev.row, prev.col, direction, dist)
  # assert (0 <= r < len(grid) and 0 <= c < len(grid[0]))
  
  cell = grid[r][c]
  entry_axis = dirAxis(direction)
  node = cell[entry_axis]
  #assert node.entry_axis == entry_axis
  
  path_cost = prev.best + extra_cost
  if path_cost >= node.best:
    return

  # print(f'improve ({r},{c},{axisName(entry_axis)}) {bestStr(node.best)}->{path_cost}')
  
  node.best = path_cost
  node.prev = prev
  # print(f'  relax {r},{c} from direction {direction}')
  node.entry_direction = direction
  node.entry_run = dist
  node_heap.decreaseKey(node)


def printPath(grid_orig):
  # create another grid where each node is [move, cost]
  # and move is one of ' ', '^', '>', 'v', '<'
  grid = []
  for row in grid_orig:
    grid.append([[' ', e[0].cost] for e in row])

  r = len(grid_orig)-1
  c = len(grid_orig[0])-1
  total_cost = 0

  cell = grid_orig[r][c]
  if cell[AXIS_HORIZ].best < cell[AXIS_VERT].best:
    entry_axis = AXIS_HORIZ
  else:
    entry_axis = AXIS_VERT
  node = cell[entry_axis]
  
  while r > 0 or c > 0:
    assert dirAxis(node.entry_direction) == entry_axis
    back_direction = invDir(node.entry_direction)
    dir_char = dirChar(node.entry_direction)
    for i in range(node.entry_run):
      total_cost += grid_orig[r][c][0].cost
      grid[r][c][0] = dir_char
      r,c = move(r, c, back_direction)
    entry_axis = 1 - entry_axis
    prev = grid_orig[r][c][entry_axis]
    assert prev == node.prev
    node = prev

  for row in grid:
    print(' '.join([f'{e[0]}{e[1]}' for e in row]))

  print(f'total cost {total_cost}')
  

# testHeap()

def part1(filename):
  grid = readInput(filename)
  height = len(grid)
  width = len(grid[0])

  dijkstra(grid, 1, 3)

  end = grid[height-1][width-1]
  best = min(end[0].best, end[1].best)
  print(f'part1 {best}')

  # print(grid[height-1][width-1][0])
  # print(grid[height-1][width-1][1])
  # printPath(grid)
  

def part2(filename):
  grid = readInput(filename)
  height = len(grid)
  width = len(grid[0])

  dijkstra(grid, 4, 10)

  end = grid[height-1][width-1]
  best = min(end[0].best, end[1].best)
  print(f'part2 {best}')

  # print(grid[height-1][width-1][0])
  # print(grid[height-1][width-1][1])
  # printPath(grid)

if __name__ == '__main__':
  filename = 'day17.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)


