#!/usr/bin/env python3

"""
Advent of Code 2023, day 23: A Long Walk

Flood fill and finding longest weighted path in a graph.

My solution for part2 converts the maze into a graph and tests every
possible path, which is slow (40 seconds on my laptop). How to speed
it up? As far as I can tell, since this is an undirected cyclic graph
it's an NP-Hard problem so there isn't an efficient solution. There's
probably a trick somewhere.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, collections, random, time
from common import *
from draw_grid import drawGrid



class Vertex:
  def __init__(self, index, name, coord):
    self.index = index
    self.name = name
    self.coord = coord
    self.outgoing_directions = []
    self.edges = set()
    self.visited = False

  def __str__(self):
    return str(self.index)


class Edge:
  def __init__(self, index, start_coord = None):
    self.index = index
    self.weight = None
    self.start_coord = start_coord
    self.end_coord = None
    self.vertices = []

    # choose a random light color
    self.color = (random.randint(50, 255), random.randint(50, 255),
                  random.randint(50, 255))

  def __str__(self):
    return f'{self.index}({self.weight})'

  def addVertex(self, r, c):
    coord = (r,c)
    if coord not in self.vertices:
      self.vertices.append(coord)

  def otherEnd(self, vertex):
    """
    Given one of this edge's vertices, return the other one.
    """
    if vertex == self.vertices[0]:
      return self.vertices[1]
    else:
      assert self.vertices[1] == vertex
      return self.vertices[0]



class Graph:
  def __init__(self):
    self.vertices = []
    self.edges = []

    # coordinate -> Vertex
    self.vertex_table = {}

  def createVertex(self, coord):
    """
    Creates a new vertex and returns it.
    """
    index = len(self.vertices)
    v = Vertex(index, f'v{index}', coord)
    self.vertices.append(v)
    self.vertex_table[coord] = v
    return v

  
  def createEdge(self, start_coord):
    index = len(self.edges)
    e = Edge(index, start_coord)
    self.edges.append(e)
    return e


  def writeGraphViz(self, filename):
    with open(filename, 'w') as outf:
      outf.write('graph day23 {\n')
      
      outf.write(f'  n{self.vertices[0]} [shape=Mdiamond];\n')
      outf.write(f'  n{self.vertices[1]} [shape=Msquare];\n')

      for edge in self.edges:
        outf.write(f'  n{edge.vertices[0].index} -- n{edge.vertices[1].index} [label={edge.weight}]\n')
          
      outf.write('}\n')
    print(f'wrote {filename}')


def part1(filename):
  with open(filename) as inf:
    grid = readGrid(inf, True)
  assert grid[0][1] == '.'

  # drawGrid(grid, 'day23.png',
  #          {'>': (0,255,0),  # right green
  #           'v': (0,0,255),  # down blue
  #           })

  # drawGrid(grid, 'day23b.png',
  #          {'>': (255,255,255),
  #           'v': (255,255,255),
  #           })
  
  path_lengths = findAllPathLengths(grid)

  path_lengths.sort()
  print(f'part1 {path_lengths[-1]}')


def part2(filename):
  with open(filename) as inf:
    orig_grid = readGrid(inf, True)
  colored_grid = createGrid(len(orig_grid), len(orig_grid[0]), True)
  for r, row in enumerate(orig_grid):
    for c, e in enumerate(row):
      if e == '>' or e == 'v':
        e = '.'
      colored_grid[r][c] = e
        
  # Traverse the grid and define a connectivity graph.
  # A node in the graph is a set of cells that are connected and have no
  # intersections.
  # An intersection is a set of edges in the graph, connecting
  # the three or four nodes that represent the paths from the intersection.

  graph = buildGraph(colored_grid)

  """
  grid_colors = {'+': (255,0,0)}
  for node in graph.nodes:
    grid_colors[node.index] = node.color
  drawGrid(colored_grid, 'day23.colored.png', grid_colors)
  """
  # graph.writeGraphViz('day23.gv')
  # neato -Tpdf -oday23.pdf day23.gv

  findHeaviestPath(graph)
  

def dirList(cell):
  return ' '.join([direction_names[x] for x in cell[3:]])


def cellStr(cell):
  return f'{cell[0]},{cell[1]} {dirList(cell)}'


def findAllPathLengths(grid):
  """
  Do a DFS traversal of the routes through the grid, adding
  the length of each solution to path_lengths.

  '#' is a wall
  '.' is traversible
  '>' cannot be traversed going LEFT
  'v' cannot be traversed going UP
  There are no '<' or '^' cells in the input data.
  """

  solution_lengths = []

  """
  Each entry in path is a list containing at least three elements, the row
  and column coordinates, and the original cell entry ('.', '>', or 'v').
  There can be up to two more elements, and those
  will be directions not explored yet.
  For example:
    [0, 1, '.']
    [10, 20, '>', DOWN, LEFT]
  """
  path = collections.deque()

  r, c = 0, 1
  grid[r][c] = 'O'
  path.append([r, c, '.', DOWN])

  available_directions = []
  solution_row = len(grid)-1

  # while r != None and c != None:

  while len(path) > 0:

    prev = path[-1]
    # print(f'prev = {repr(prev)}')
    direction = prev[-1]
    del(prev[-1])
    r,c = move(prev[0], prev[1], direction)
    
    # print('  ' + direction_names[direction])
    
    cell = [r, c, grid[r][c]]
    grid[r][c] = 'O'
    path.append(cell)
    # print(f'at {r}, {c}')

    if r == solution_row:
      solution_lengths.append(len(path)-1)
      # print(f'  solution of length {solution_lengths[-1]} found')
      backtrack(path, grid)
      continue

    # cell contains [r, c]. Append available directions to it.
    # For example [r, c, RIGHT, DOWN, LEFT]
    appendAvailableDirections(r, c, grid, cell)
    if len(cell) == 3:
      backtrack(path, grid)
      continue
    
    # printPath(path)

    # if len(cell) > 4:
    #   print('fork: ' + cellStr(cell))

    # direction = cell[-1]
    # del(cell[-1])
    # r,c = move(r, c, direction)

  return solution_lengths


def printPath(path):
  for entry in path:
    dir_list = ' '.join([direction_names[x] for x in entry[3:]])
    print(f'  {entry[0]},{entry[1]} {dir_list}')


def backtrack(path, grid):
  """
  Backtrack, erasing our path from the grid, until either we're back
  at the starting cell or we're at a cell with more directions to explore.

  If this backtracks to the starting cell, this returns (None, None).

  Otherwise, entries will be removed from right end path until one is
  found with more that two elements, where the third and possibly fourth
  elements are directions to explore. It will remove one of those elements,
  apply that direction of motion to the coordinates in that entry,
  and return the coordinates in that direction.
  """

  # print('backtracking')
  # print('backtracking, current path:')
  # printPath(path)
  
  steps_erased = 0
  while len(path) > 0 and len(path[-1]) < 4:
    r,c,f = path.pop()
    grid[r][c] = f
    steps_erased += 1

  # printGrid(grid)

  if len(path) == 0:
    return False
    # return None, None

  last = path[-1]
  direction = last[-1]
  # print(f'backtrack {steps_erased} steps to {last[0]},{last[1]}, going {direction_names[direction]}')
  return True


def appendAvailableDirections(r, c, grid, cell):
  if r>0 and grid[r-1][c] == '.':
    cell.append(UP)
  if grid[r][c+1] == '.' or grid[r][c+1] == '>':
    cell.append(RIGHT)
  if r < len(grid)-1 and (grid[r+1][c] == '.' or grid[r+1][c] == 'v'):
    cell.append(DOWN)
  if grid[r][c-1] == '.':
    cell.append(LEFT)


def fillDirection2(grid, edge, r, c):
  """
  While filling a region, after intersections have all been marked with
  a '+', there should be one or zero adjoining empty cells (contain '.').
  Return the empty direction or None if there's a dead end.
  
  Also, feed each intersection found to edge.addVertex()
  """
  if r>0:
    if grid[r-1][c] == '+':
      edge.addVertex(r-1, c)
    elif grid[r-1][c] == '.':
      return UP
    
  if grid[r][c+1] == '+':
    edge.addVertex(r, c+1)
  elif grid[r][c+1] == '.':
    return RIGHT

  if r < len(grid)-1:
    if grid[r+1][c] == '+':
      edge.addVertex(r+1, c)
    elif grid[r+1][c] == '.':
      return DOWN
    
  if grid[r][c-1] == '+':
    edge.addVertex(r, c-1)
  elif grid[r][c-1] == '.':
    return LEFT

  return None


def fillDirection(grid, r, c):
  """
  While filling a region, after intersections have all been marked with
  a '+', there should be one or zero adjoining empty cells (contain '.').
  Return the empty direction or None if there's a dead end.
  """
  if r>0 and grid[r-1][c] == '.': return UP
  if grid[r][c+1] == '.': return RIGHT
  if r < len(grid)-1 and grid[r+1][c] == '.': return DOWN
  if grid[r][c-1] == '.': return LEFT
  return None


def appendIfIntersection(grid, ict, r, c):
  if r >= 0 and r < len(grid) and grid[r][c] == '+':
    ict.add((r,c))

def adjacentIntersections(grid, ict, r, c):
  appendIfIntersection(grid, ict, r-1, c)
  appendIfIntersection(grid, ict, r, c+1)
  appendIfIntersection(grid, ict, r+1, c)
  appendIfIntersection(grid, ict, r, c-1)


def isIntersection(grid, r, c):
  count = 0
  if grid[r][c] != '.': return False
  if grid[r-1][c] == '.': count += 1
  if grid[r][c+1] == '.': count += 1
  if grid[r+1][c] == '.': count += 1
  if grid[r][c-1] == '.': count += 1
  return count > 2


def outgoingDirections(grid, r, c):
  """
  Assuming this is an intersection, return a list of the outgoing directions.
  """
  dirs = []
  assert grid[r][c] == '.'
  if grid[r-1][c] == '.': dirs.append(UP)
  if grid[r][c+1] == '.': dirs.append(RIGHT)
  if grid[r+1][c] == '.': dirs.append(DOWN)
  if grid[r][c-1] == '.': dirs.append(LEFT)
  assert len(dirs) >= 3 and len(dirs) <= 4
  return dirs


def fillRegion(grid, graph, r, c):
  """
  If (r,c) is empty create a new edge region and fill it with a random color.
  Stop when an intersection or dead end is found.
  Intersections will be filled in with '+'
  """

  # already full
  if grid[r][c] != '.':
    # print(f'at {r},{c} already filled')
    return None

  edge = graph.createEdge((r, c))
  edge.weight = 0
  # grid[r][c] = edge.index
  # prev_r, prev_c = r, c

  # print(f'Edge {edge.index} fill at {r},{c}')

  while True:
    assert grid[r][c] == '.'
    grid[r][c] = edge.index
    edge.weight += 1

    direc = fillDirection(grid, r, c)

    if direc == None:
      edge.end_coord = (r,c)
      # print(f'  end at {r},{c} weight {edge.weight}')
      break

    r,c = move(r, c, direc)

  # find vertices
  # they will be adjacent to my start and end coordinates
  assert isinstance(edge.start_coord, tuple)
  assert isinstance(edge.end_coord, tuple)

  adjacent_ict = set()
  if edge.start_coord[0] in [0, len(grid)-1]:  # start or end vertex
    adjacent_ict.add(edge.start_coord)
  adjacentIntersections(grid, adjacent_ict, *edge.start_coord)
  adjacentIntersections(grid, adjacent_ict, *edge.end_coord)
  if len(adjacent_ict) != 2:
    print(f'Error edge {edge.index} {edge.start_coord[0]},{edge.start_coord[1]}-{edge.end_coord[0]},{edge.end_coord[1]} adjacent intersection list: {adjacent_ict!r}')
  else:
    assert len(edge.vertices) == 0
    for coord in adjacent_ict:
      vtx = graph.vertex_table.get(coord, None)
      if not vtx:
        print(f'Error edge {edge.index} adjacent vertex at {coord!r} not found')
      else:
        edge.vertices.append(vtx)
        vtx.edges.add(edge)
        # print(f'  edge {edge.index} vertex {vtx.index}')
  
  return edge  


def buildGraph(grid):
  graph = Graph()
  r,c = 0,1

  # Each intersection in the grid is a vertex in the graph.
  # Corridors between intersections or the entry and exit points
  # are edges where their weight is their length.

  start_col = grid[0].index('.')
  start_vertex = graph.createVertex((0, start_col))

  end_col = grid[-1].index('.')
  end_vertex = graph.createVertex((len(grid)-1, end_col))
  
  # first scan the grid for all intersections
  for r in range(1, len(grid)-1):
    for c in range(1, len(grid[r])-1):
      if isIntersection(grid, r, c):
        vertex = graph.createVertex((r,c))
        vertex.outgoing_directions = outgoingDirections(grid, r, c)
        grid[r][c] = '+'
        # print(f'vertex {vertex.index} at {r},{c}')

  # If the given region is empty, fillRegion will fill it and
  # create and Edge for it.
  edge = fillRegion(grid, graph, *start_vertex.coord)
  edge = fillRegion(grid, graph, *end_vertex.coord)
  for vertex in graph.vertices:
    for d in vertex.outgoing_directions:
      r,c = move(*vertex.coord, d)
      fillRegion(grid, graph, r, c)

      
      # print(f'edge {edge.index}:   {edge.start_coord[0]},{edge.start_coord[1]}-{edge.end_coord[0]},{edge.end_coord[1]} weight {edge.weight} from {edge.start_vertex} to {edge.end_vertex}')
          
  return graph


def findHeaviestPath(graph):
  start_vertex, end_vertex = graph.vertices[:2]

  vertex = start_vertex
  heaviest_path = [0]
  path = [vertex]

  # the first and last edges are shorted by the '+' at the start/end
  weight = -2
  
  findHeaviestRecurse(graph, path, heaviest_path, vertex, weight)
  print(f'part2 {heaviest_path[0]}')


def findHeaviestRecurse(graph, path, heaviest_path, vertex, weight):
  # assert not vertex.visited

  # graph.vertices[1] is end vertex
  if vertex == graph.vertices[1]:
    # path_str = ' '.join([str(v) for v in path])
    # print(f'{weight} path {path_str}')
    if weight > heaviest_path[0]:
      heaviest_path[0] = weight
      # ts = time.strftime('%H:%M:%S', time.localtime())
      # print(f'{ts} heaviest found {weight}')
    return

  for edge in vertex.edges:
    vnext = edge.otherEnd(vertex)
    if not vnext.visited:
      path.append(vnext)
      vnext.visited = True
      findHeaviestRecurse(graph, path, heaviest_path, vnext,
                          weight + edge.weight + 1)
      vnext.visited = False
      path.pop()


if __name__ == '__main__':
  filename = 'day23.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
  
