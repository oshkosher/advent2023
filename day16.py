#!/usr/bin/env python

"""
Advent of Code 2023, day 16: The Floor Will Be Lava

Follow reflecting and splitting light beams.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, collections

DIR_RIGHT = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_UP = 3


dir_offsets = [(0,1),  # right
               (1,0),  # down
               (0,-1), # left
               (-1,0)] # up


class LightBeam:
  def __init__(self, row, col, direction):
    self.row = row
    self.col = col
    # 0..3
    assert(0 <= direction < 4)
    self.direction = direction

  def __str__(self):
    dir_name = ['right', 'down', 'left', 'up']
    return f'beam({self.row},{self.col},{dir_name[self.direction]})'

  def copy(self):
    return LightBeam(self.row, self.col, self.direction)

  def move(self):
    offset = dir_offsets[self.direction]
    self.row += offset[0]
    self.col += offset[1]

  def isOffGrid(self, grid):
    return (self.row < 0 or self.col < 0
            or self.row >= len(grid) or self.col >= len(grid[0]))
                            
    
class Tile:
  def __init__(self, lens):
    self.lens = lens
    if lens not in ['.', '|', '-', '/', '\\']:
      print(f'error: unrecognized lens {repr(lens)}')
      sys.exit(1)

    self.is_energized = False

    # marks whether a beam in this direction has been traversed
    self.beams = [False] * 4

  def __str__(self):
    return '#' if self.is_energized else '.'

  def reset(self):
    self.is_energized = False
    self.beams = [False] * 4
    

def readInput(filename):
  with open(filename) as inf:
    grid = []
    for line in inf:
      line = line.strip()
      if not line: continue
      grid.append([Tile(x) for x in line])
  return grid


def resetGrid(grid):
  for row in grid:
    for tile in row:
      tile.reset()

def countEnergized(grid):
  count = 0
  for row in grid:
    for tile in row:
      if tile.is_energized: count += 1
  return count

def printGrid(grid):
  for row in grid:
    s = ''.join([c.lens for c in row])
    print(s)


def printEnergizedTiles(grid):
  for row in grid:
    s = ''.join([str(tile) for tile in row])
    print(s)
  

def printTraversal(grid):
  """
  Make each cell 2 characters wide. The first character is the lens,
  the second character is '*' if it is energized.
  """
  for row in grid:
    for tile in row:
      energized = '*' if tile.is_energized else ' '
      sys.stdout.write(tile.lens + energized)
    sys.stdout.write('\n')


def isPassThrough(direction, lens):
  if lens == '.':
    return True
  elif lens == '/' or lens == '\\':
    return False
  elif lens == '|':
    return direction == DIR_UP or direction == DIR_DOWN
  elif lens == '-':
    return direction == DIR_LEFT or direction == DIR_RIGHT
  else:
    raise Exception(f'Invalid lens "{lens}"')


def outgoingDirections(direction, lens):
  """
  Return a list of the outgoing directions.
  With an empty cell or a splitter edge-on, the direction is unchanged.
  With a mirror, the new direction is returned.
  With a splitter face-on, the two new directions are returned.
  """
  if isPassThrough(direction, lens):
    return [direction]

  if lens == '/':
    return [[DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT][direction]]

  elif lens == '\\':
    return [[DIR_DOWN, DIR_RIGHT, DIR_UP, DIR_LEFT][direction]]

  elif lens == '|':
    return [DIR_DOWN, DIR_UP]

  elif lens == '-':
    return [DIR_LEFT, DIR_RIGHT]
  

def traverse(grid, light_beam_queue):
  """
  The current position of each light beam has not yet been marked as lighted.
  """
  while len(light_beam_queue) > 0:
    beam = light_beam_queue.popleft()
    if beam.isOffGrid(grid):
      # print('  off grid: ' + str(beam))
      continue
    
    tile = grid[beam.row][beam.col]

    # we've already been here
    if tile.beams[beam.direction]:
      # print('  already traversed: ' + str(beam))
      continue

    # print('mark ' + str(beam))
    tile.is_energized = True
    tile.beams[beam.direction] = True

    beam2 = None
    outgoing = outgoingDirections(beam.direction, tile.lens)
    assert 1 <= len(outgoing) <= 2
    if len(outgoing) > 1:
      beam2 = beam.copy()

    beam.direction = outgoing[0]
    beam.move()
    light_beam_queue.append(beam)

    if beam2:
      beam2.direction = outgoing[1]
      beam2.move()
      light_beam_queue.append(beam2)

    # print(f'  {len(light_beam_queue)} beams in flight')
    # printTraversal(grid)
  
def part1(filename):
  grid = readInput(filename)
  # printGrid(grid)

  light_beam_queue = collections.deque()
  light_beam_queue.append(LightBeam(0, 0, 0))

  traverse(grid, light_beam_queue)
  # printEnergizedTiles(grid)

  print(f'part1 {countEnergized(grid)}')


def testStartingPoint(grid, row, col, direction):
  # returns the number of energized tiles

  resetGrid(grid)
  light_beam_queue = collections.deque()
  light_beam_queue.append(LightBeam(row, col, direction))
  traverse(grid, light_beam_queue)
  return countEnergized(grid)
  

def part2(filename):
  grid = readInput(filename)

  max_energized = 0

  height = len(grid)
  width = len(grid[0])

  for c in range(width):
    # top row
    count = testStartingPoint(grid, 0, c, DIR_DOWN)
    # print(f'  {c}  down: {count}')
    max_energized = max(max_energized, count)

    # bottom row
    count = testStartingPoint(grid, height-1, c, DIR_UP)
    # print(f'  {c}    up: {count}')
    max_energized = max(max_energized, count)
    
  for r in range(height):
    # left column
    count = testStartingPoint(grid, r, 0, DIR_RIGHT)
    # print(f'  {r} right: {count}')
    max_energized = max(max_energized, count)

    # right column
    count = testStartingPoint(grid, r, width-1, DIR_LEFT)
    # print(f'  {r}  left: {count}')
    max_energized = max(max_energized, count)

  print(f'part2 {max_energized}')


if __name__ == '__main__':
  filename = 'day16.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)


