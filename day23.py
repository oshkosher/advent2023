#!/usr/bin/env python3

"""
Advent of Code 2023, day 23: A Long Walk

Flood fill and finding longest weighted path in a graph.

My solution for part2 converts the maze into a graph and tests every
possible path, which is slow (40 seconds on my laptop). How to speed
it up? As far as I can tell, since this is an undirected cyclic graph
it's an NP-Hard problem so there isn't an efficient solution. There's
probably a trick somewhere.

One nice trick comes from the fact that because the graph is based
on a flat 2-d maze, edges cannot cross each other. Which means once you
traverse a path that runs along the perimeter, you can only continue
towards the endpoint; you cannot backtrack along the perimeter.

The graph ends up looking like this:

Start >  a > b > c > d > e
         v   |   |   |   | \
         f - A - B - C - D - g
         v   |   |   |   |   v
         h - E - F - G - H - k
         v   |   |   |   |   v
         m - K - M - N - P - n
         v   |   |   |   |   v
         p - Q - R - S - T - q
           \ |   |   |   |   v
             r > s > t > u > v > End

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, collections, random, time
from common import *
from draw_grid import drawGrid


class Edge:
  def __init__(self, index):
    self.index = index
    self.vertices = []
    self.length = None

    # if is_directed then can only traverse from vertices[0]->vertices[1],
    # not vertices[1]->vertices[0].
    self.is_directed = False

    # choose a random light color
    min_c = 100
    self.color = (random.randint(min_c, 255), random.randint(min_c, 255),
                  random.randint(min_c, 255))

  def addVertex(self, vertex):
    if vertex not in self.vertices:
      assert len(self.vertices) < 2
      self.vertices.append(vertex)

  def otherVertex(self, vertex):
    if len(self.vertices) != 2:
      return None

    if self.vertices[0] == vertex:
      return self.vertices[1]

    if self.is_directed:
      return None

    if self.vertices[1] == vertex:
      return self.vertices[0]

    return None

  def setIsDirected(self, src_vertex):
    """
    Set this edge to be directed and with src_vertex as the incoming vertex.
    """
    assert src_vertex in self.vertices
    if self.vertices[1] == src_vertex:
      self.vertices.reverse()
    self.is_directed = True
    # print(f'set edge {self.index} directed {self.vertices[0].index} -> {self.vertices[1].index}')

  def __repr__(self):
    return f'Edge({self.index},len={self.length})'


class Vertex:
  def __init__(self, index, r, c):
    self.index = index
    self.coord = (r,c)
    self.edges = []
    self.visited = False

  def addEdge(self, edge):
    if edge not in self.edges:
      self.edges.append(edge)

  def coordStr(self):
    return f'{self.coord[0]},{self.coord[1]}'

  def findEdgeTo(self, dest_vertex):
    for edge in self.edges:
      vtx = edge.otherVertex(self)
      if vtx == dest_vertex:
        return edge
    return None

  def __repr__(self):
    edge_list = ','.join([str(e.index) for e in self.edges])
    return f'Vertex({self.index} at {self.coord[0]},{self.coord[1]} edges {edge_list})'
    

class Graph:
  def __init__(self):
    # coord -> Vertex
    self.vertices = {}
    
    self.edges = []

  def createEdge(self):
    index = len(self.edges)
    edge = Edge(index)
    self.edges.append(edge)
    return edge

  def createVertex(self, r, c):
    coord = (r,c)
    vertex = self.vertices.get(coord, None)
    if not vertex:
      index = len(self.vertices)
      vertex = Vertex(index, r, c)
      self.vertices[coord] = vertex
    return vertex

  def connect(self, vertex, edge):
    vertex.addEdge(edge)
    edge.addVertex(vertex)

  def clearVisited(self):
    for vertex in self.vertices.values():
      vertex.visited = False

  def print(self):
    print('graph edges')
    for edge in self.edges:
      vertex_list = ' '.join([str(v.index) for v in edge.vertices])
      print(f'  {edge} vertices {vertex_list}')
    print('graph vertices')
    for vertex in self.vertices.values():
      print(f'  {vertex}')

  def writeGraphViz(self, filename):
    with open(filename, 'w') as outf:
      outf.write('digraph day23 {\n')

      first_vertex = self.edges[0].vertices[0]
      last_vertex = self.edges[1].vertices[0]
      
      outf.write(f'  n{first_vertex.index} [shape=Mdiamond];\n')
      outf.write(f'  n{last_vertex.index} [shape=Msquare];\n')

      for edge in self.edges:
        if len(edge.vertices) >= 2:
          tag = '' if edge.is_directed else '[dir=none]'
          outf.write(f'  n{edge.vertices[0].index} -> n{edge.vertices[1].index} [label={edge.length}] {tag}\n')

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


def entryTraverse(grid, r, c, edge):
  """
  Start traversing from (r,c), which is either the entry or the exit.
  Fill each cell with the value (edge) until an intersection is found.
  Fill the intersection with '+'.
  Return the coordinates of the intersection and the length of the traverse.
  For example: [r, c, length]

  At each point in the traversal, these are the cases which may be encountered:
  a) 2 directions are walls, 1 direction is my color, 1 direction is empty
     (or '>' or '<'). Fill with my color and proceed in the empty direction.
  b) 1 direction is a wall, 1 direction is my color, 2 directions is empty
     This is an intersection. Mark it with a '+' and return.
  """

  # handle the first step manually so we don't have to check bounds again.
  assert r == 0 or r == len(grid)-1
  # print(f'entry traverse from {r},{c} edge {edge}')
  grid[r][c] = edge
  if r == 0:
    r += 1
  else:
    r -= 1
  length = 1

  nonempty = ['#', edge]

  available_directions = []

  def tryDirection(r, c, d):
    r,c = move(r, c, d)
    if grid[r][c] not in nonempty:
      available_directions.append(d)

  while True:
    available_directions.clear()
    for direction in range(1, 5):
      tryDirection(r, c, direction)
    assert 1 <= len(available_directions) <= 2
    if len(available_directions) == 1:
      length += 1
      grid[r][c] = edge
      r, c = move(r, c, available_directions[0])
    else:
      # intersection found
      # print(f'  end at {r},{c} length {length}')
      return [r, c, length]


def interiorTraverse(grid, r, c, incoming_direction, edge):
  """
  Traverse from a known intersection to the next intersection, known or not.
  Returns the coordinates of that intersection and the length of the traverse:
    [r, c, length]

  For this traversal, we consider an adjacent '+' an empty cell,
  and '#' or my edge a full cell.

  Special-case the start, to get started in the right direction,
  since it will look like a corridor with adjacent cells +, #, ., #.
  Also check for a length-1 corridor "+.+".
  
  At each point in the traversal, these are the cases which may be encountered:
    1 empty (continue on)
    2 empty (3-way intersection found)
    3 empty (4-way intersection found)
  we should never run into a dead end with these mazes.
  """

  # check that my incoming direction was set correctly
  origin_r, origin_c = move(r, c, invDir(incoming_direction))
  assert '+' == grid[origin_r][origin_c]

  # print(f'interiorTraverse edge {edge.index} {direction_names[incoming_direction]} from {edge.vertices[0]}')
  
  empty_directions = []

  nonempty = ['#', edge]
  
  def tryDirection(r, c, d):
    r,c = move(r, c, d)
    if grid[r][c] not in nonempty:
      empty_directions.append(d)


  # first cell
  assert grid[r][c] in ['.', '>', 'v']
  length = 1
  grid[r][c] = edge
  for direction in range(1, 5):
    tryDirection(r, c, direction)
  assert len(empty_directions) == 2
  assert incoming_direction in empty_directions
  assert invDir(incoming_direction) in empty_directions
  r,c = move(r, c, incoming_direction)
  if grid[r][c] == '+':
    # completed intersections at both ends, length == 1
    # print('  single-cell edge')
    return r, c, length
  
  while True:
    empty_directions.clear()
    for direction in range(1, 5):
      tryDirection(r, c, direction)

    if len(empty_directions) == 1:
      length += 1
      grid[r][c] = edge
      r,c = move(r, c, empty_directions[0])
    else:
      # print(f'  end at {r},{c} length {length}')
      return [r, c, length]


def makePerimeterDirectional(graph):
  first_edge = graph.edges[0]
  first_vertex = first_edge.vertices[0]
  last_vertex = graph.edges[1].vertices[0]

  def nextPerimeterVertex(vertex):
    for edge in vertex.edges:
      nv = edge.otherVertex(vertex)
      if nv and len(nv.edges) == 3:
        return (edge, nv)
    return None

  assert len(first_vertex.edges) == 3
  for edge in first_vertex.edges:
    if edge != first_edge:
      edge.setIsDirected(first_vertex)
      vertex = edge.otherVertex(first_vertex)
      while True:
        (edge, nv) = nextPerimeterVertex(vertex)
        edge.setIsDirected(vertex)
        if nv == last_vertex:
          break
        vertex = nv


def buildGraph(grid):
  """
  Build graph more cleanly.

  Start with a special traverse from the entrance to the first intersection,
  then from the exit to the last intersection.

  During traversals, silenty overwrite one-way marks ">" and "v" as empty "."
  Fill each spot with an integer for the edge index.
  """
  graph = Graph()

  # verify entry and exit
  exit_r = len(grid)-1
  exit_c = len(grid[0])-2
  assert grid[0][1] == '.' and grid[exit_r][exit_c] == '.'

  # each entry is a Vertex object
  isect_to_traverse = collections.deque()

  entry_edge = graph.createEdge()
  ir, ic, entry_edge.length = entryTraverse(grid, 0, 1, entry_edge)
  isect = graph.createVertex(ir, ic)
  graph.connect(isect, entry_edge)
  isect_to_traverse.append(isect)
  
  exit_edge = graph.createEdge()
  ir, ic, exit_edge.length = entryTraverse(grid, exit_r, exit_c, exit_edge)
  isect = graph.createVertex(ir, ic)
  graph.connect(isect, exit_edge)
  isect_to_traverse.append(isect)

  empty = ['.', '>', 'v']

  while isect_to_traverse:
    isect = isect_to_traverse.popleft()
    ir,ic = isect.coord
    if grid[ir][ic] == '+':
      continue

    grid[ir][ic] = '+'
    # print(f'traverse {isect}')
    
    for d in range(1, 5):
      r,c = move(ir, ic, d)
      cell = grid[r][c]
      if cell in empty:
        edge = graph.createEdge()
        graph.connect(isect, edge)
        nr, nc, edge.length = interiorTraverse(grid, r, c, d, edge)
        next_isect = graph.createVertex(nr, nc)
        graph.connect(next_isect, edge)
        isect_to_traverse.append(next_isect)
      elif cell != '#':
        assert isinstance(cell, Edge)
        graph.connect(isect, cell)
        
  return graph


class TraverseData:
  def __init__(self, graph, start_vertex, end_vertex):
    self.graph = graph
    self.start_vertex = start_vertex
    self.end_vertex = end_vertex
    self.path = [self.start_vertex]
    self.max_weight = 0
    self.max_path = []
    self.start_time = time.time()
    self.paths_found = 0

  def pathStr(self, path):
    edge = self.graph.edges[0]
    vertex = self.start_vertex
    path_str = [str(edge.length), '(' + vertex.coordStr() + ')']
    for vi in range(1, len(path)):
      prev = path[vi-1]
      next = path[vi]
      edge = prev.findEdgeTo(next)
      path_str.append(str(edge.length))
      path_str.append('(' + next.coordStr() + ')')
    edge = self.graph.edges[1]
    path_str.append(str(edge.length))
    return '-'.join(path_str)



def findHeaviestPath(graph):
  assert isinstance(graph, Graph)

  first_edge, last_edge = graph.edges[:2]
  assert len(first_edge.vertices) == 1
  assert len(last_edge.vertices) == 1

  start_vertex = first_edge.vertices[0]
  start_vertex.visited = True
  trav = TraverseData(graph, start_vertex, last_edge.vertices[0])

  weight = first_edge.length + last_edge.length
  timer = time.time()

  findHeaviestRecurse(trav, start_vertex, weight, 0)
  start_vertex.visited = False

  # print(f'traverse time {time.time() - trav.start_time:.3f} sec')
  # print(f'{trav.paths_found} paths found')
  # print(f'part2 {trav.max_weight} {trav.pathStr(trav.max_path)}')
  print(f'part2 {trav.max_weight}')


def findHeaviestRecurse(trav, vertex, weight, depth):
  # assert not vertex.visited

  # vertex = trav.path[-1]
  # print(f'{"  " * depth} fh {vertex}')
  
  # graph.vertices[1] is end vertex
  if vertex == trav.end_vertex:
    # print(f'{weight} path {trav.pathStr(trav.path)}')
    trav.paths_found += 1
    if weight > trav.max_weight:
      trav.max_weight = weight
      # trav.max_path = trav.path.copy()
      # print(f'{time.time() - trav.start_time:.3f} heaviest found {weight}')
    return

  for edge in vertex.edges:
    vnext = edge.otherVertex(vertex)
    if vnext and not vnext.visited:
      # trav.path.append(vnext)
      vnext.visited = True
      findHeaviestRecurse(trav, vnext, weight + edge.length + 1, depth + 1)
      vnext.visited = False
      # trav.path.pop()


def part2(filename):
  with open(filename) as inf:
    grid = readGrid(inf, True)

  """
  for row in grid:
    for c in range(len(row)):
      if row[c] == '>': row[c] = '.'
      if row[c] == 'v': row[c] = '.'
  """

  """
  drawGrid(grid, 'day23.png',
           {'>': (0,255,0),  # right green
            'v': (0,0,255),  # down blue
            })
  """
    
  graph = buildGraph(grid)
  # graph.print()

  # this makes it 3.3x faster, even though the same number of complete
  # paths are found; it's just less backtracking
  makePerimeterDirectional(graph)
  
  # graph.writeGraphViz('day23.gv')
  
  """
  color_table = {e: e.color for e in graph.edges}
  color_table['+'] = (255, 0, 0)
  drawGrid(grid, 'day23b.png', color_table)
  """
  
  findHeaviestPath(graph)


if __name__ == '__main__':
  filename = 'day23.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
