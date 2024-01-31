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

import sys, collections, random, time, copy
from common import *
# from draw_grid import drawGrid

FLOW_BI = 0
FLOW_FORE = 1
FLOW_BACK = 2


class Vertex:
  def __init__(self, index, r, c):
    self.index = index
    self.coord = (r,c)
    self.visited = False

    # reachable vertices, with edge length
    # (vertex, length)
    self.peers = []

  def findPeer(self, vertex):
    for i, peer in enumerate(self.peers):
      if peer[0] == vertex:
        return i
    return -1

  def addPeer(self, vertex, length):
    if -1 == self.findPeer(vertex):
      self.peers.append((vertex, length))

  def removePeer(self, vertex):
    i = self.findPeer(vertex)
    assert i > -1
    del(self.peers[i])

  def makeBiDirectional(self):
    for peer, length in self.peers:
      peer.addPeer(self, length)

  def coordStr(self):
    return f'{self.coord[0]},{self.coord[1]}'

  def __repr__(self):
    peer_list = ', '.join([f'{length}->{dest.index}' for dest,length in self.peers])
    return f'Vertex({self.index} at {self.coord[0]},{self.coord[1]}: {peer_list})'
    

class Graph:
  def __init__(self):
    self.vertex_list = []
    
    # coord -> Vertex
    self.vertex_map = {}
    
    self.entry_edge_len = None
    self.exit_edge_len = None


  def createVertex(self, r, c):
    coord = (r,c)
    vertex = self.vertex_map.get(coord, None)
    if not vertex:
      # index = len(self.vertex_list)
      
      # set vertex indices to powers of 2
      index = 1 << len(self.vertex_list)
      
      vertex = Vertex(index, r, c)
      self.vertex_list.append(vertex)
      self.vertex_map[coord] = vertex
    return vertex

  def connectVertices(self, vtx1, vtx2, length, flow_direction = FLOW_BI):
    if flow_direction in [FLOW_FORE, FLOW_BI]:
      vtx1.addPeer(vtx2, length)
    if flow_direction in [FLOW_BACK, FLOW_BI]:
      vtx2.addPeer(vtx1, length)

  def clearVisited(self):
    for vertex in self.vertex_list:
      vertex.visited = False
          
  def makePerimeterDirectional(self):
    first_vertex = self.vertex_list[0]
    last_vertex = self.vertex_list[1]

    def nextPerimeterVertex(src):
      # find my peer with 3 peers
      for dest,_ in src.peers:
        if dest == last_vertex or len(dest.peers) == 3:
          return dest
      return None

    assert len(first_vertex.peers) == 2
    for vertex,_ in first_vertex.peers:
      # set this edge as directed by removing peer -> first_vertex
      vertex.removePeer(first_vertex)
      while True:
        next = nextPerimeterVertex(vertex)
        next.removePeer(vertex)
        if next == last_vertex:
          break
        vertex = next

  def makeAllEdgesBiDirectional(self):
    for vertex in self.vertex_list:
      vertex.makeBiDirectional()

  def print(self):
    print('graph vertices')
    for vertex in self.vertex_list:
      print(f'  {vertex}')

  def writeGraphViz(self, filename):
    with open(filename, 'w') as outf:
      outf.write('digraph day23 {\n')

      def vertexName(v):
        return 'v' + str(v.index)

      def vertexName2(v):
        return f'v{v.index}_{v.coord[0]}_{v.coord[1]}'

      first_vertex = self.vertex_list[0]
      last_vertex = self.vertex_list[1]
      
      outf.write(f'  {vertexName(first_vertex)} [shape=Mdiamond];\n')
      outf.write(f'  {vertexName(last_vertex)} [shape=Msquare];\n')

      for vtx in self.vertex_list:
        for peer, length in vtx.peers:
          is_bi = False
          # if bidirectional, only output once
          if peer.findPeer(vtx) != -1:
            is_bi = True
            if peer.index < vtx.index:
              continue
          tag = '[dir=none]' if is_bi else ''
          outf.write(f'  {vertexName(vtx)} -> {vertexName(peer)} [label={length}] {tag}\n')

      outf.write('}\n')
    print(f'wrote {filename}')


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


def entryTraverse(grid, r, c, fill):
  """
  Start traversing from (r,c), which is either the entry or the exit.
  Fill each cell with the value (fill) until an intersection is found.
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
  # print(f'entry traverse from {r},{c} fill {fill}')
  grid[r][c] = fill
  if r == 0:
    r += 1
  else:
    r -= 1
  length = 1

  nonempty = ['#', fill]

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
      grid[r][c] = fill
      r, c = move(r, c, available_directions[0])
    else:
      # intersection found
      # print(f'  end at {r},{c} length {length}')
      return [r, c, length]


def interiorTraverse(grid, r, c, prev_direction, fill):
  """
  Traverse from a known intersection to the next intersection, known or not.
  Returns the coordinates of that intersection and the length of the traverse:
    [r, c, length, direction]

  For this traversal, we consider an adjacent '+' an empty cell,
  and '#' or my edge a full cell.

  The direction return field reports whether there were any
  directional '>' or 'v' symbols encountered. If not, it will be
  FLOW_BI.  If one ore more symbols were encountered, then if the
  traverse was in the directions of the symbols this will
  FLOW_FORE, otherwise FLOW_BACK.

  Special-case the start, to get started in the right direction,
  since it will look like a corridor with adjacent cells +, #, ., #.
  Also check for a length-1 corridor "+.+".
  
  At each point in the traversal, these are the cases which may be encountered:
    1 empty (continue on)
    2 empty (3-way intersection found)
    3 empty (4-way intersection found)
  we should never run into a dead end with these mazes.

  """
  
  empty_directions = []

  nonempty = ['#', fill]
  flow_direction = FLOW_BI
  
  def tryDirection(r, c, d):
    r,c = move(r, c, d)
    if grid[r][c] not in nonempty:
      empty_directions.append(d)

  def flowDirection(flow_direction, move_direction, cell, r, c):
    if cell == '.':
      return flow_direction

    prev_flow = flow_direction
    if cell == '>':
      # print(f'  at {r},{c} > moving {direction_names[move_direction]}')
      flow_direction = FLOW_FORE if move_direction == RIGHT else FLOW_BACK
    else:
      assert cell == 'v'
      # print(f'  at {r},{c} v moving {direction_names[move_direction]}')
      flow_direction =  FLOW_FORE if move_direction == DOWN else FLOW_BACK

    if prev_flow != FLOW_BI and flow_direction != prev_flow:
      print(f'  ERROR was flow={prev_flow} now {flow_direction}')
      
    return flow_direction
    

  # first cell
  assert grid[r][c] in ['.', '>', 'v']
  flow_direction = flowDirection(flow_direction, prev_direction, grid[r][c], r, c)
  length = 1
  grid[r][c] = fill
  for direction in range(1, 5):
    tryDirection(r, c, direction)
  assert len(empty_directions) == 2
  assert prev_direction in empty_directions
  assert invDir(prev_direction) in empty_directions
  r,c = move(r, c, prev_direction)

  # completed intersections at both ends, length == 1
  # print('  single-cell fill')
  if grid[r][c] == '+':
    return r, c, length, flow_direction
  
  while True:
    empty_directions.clear()
    for direction in range(1, 5):
      tryDirection(r, c, direction)

    if len(empty_directions) == 1:
      length += 1
      flow_direction = flowDirection(flow_direction, prev_direction, grid[r][c], r, c)
      grid[r][c] = fill
      prev_direction = empty_directions[0]
      r,c = move(r, c, prev_direction)
    else:
      # print(f'  end at {r},{c} length {length}')
      return r, c, length, flow_direction


def buildGraph(grid):
  """
  Build graph for use in part1 and part2.

  During initial traversal, mark one-way edges according to '>' and 'v' cells.

  For part2, revert all edges to bidirectional, then mark perimeter edges as one-way.
  """
  graph = Graph()

  # verify entry and exit
  exit_r = len(grid)-1
  exit_c = len(grid[0])-2
  assert grid[0][1] == '.' and grid[exit_r][exit_c] == '.'

  # queue of vertices from which to traverse outgoing hallways
  traverse_q = collections.deque()

  edge_id = 0
  ir, ic, graph.entry_edge_len = entryTraverse(grid, 0, 1, edge_id)
  start_vertex = graph.createVertex(ir, ic)
  traverse_q.append(start_vertex)

  edge_id += 1
  ir, ic, graph.exit_edge_len = entryTraverse(grid, exit_r, exit_c, edge_id)
  end_vertex = graph.createVertex(ir, ic)

  empty = ['.', '>', 'v']

  while traverse_q:
    isect = traverse_q.popleft()
    ir,ic = isect.coord

    # if this intersection has already been traversed, it will be
    # marked with a '+' in the grid
    
    if grid[ir][ic] == '+':
      continue

    # print(f'traverse {isect}')
    grid[ir][ic] = '+'
    # printGrid(grid)

    # try all outgoing directions
    for d in range(1, 5):
      r,c = move(ir, ic, d)
      cell = grid[r][c]
      if cell in empty:
        edge_id += 1
        nr, nc, length, flow_dir = interiorTraverse(grid, r, c, d, edge_id)
        next_isect = graph.createVertex(nr, nc)
        # print(f'  {direction_names[d]} {length} to {next_isect} flow={flow_dir}')
        graph.connectVertices(isect, next_isect, length, flow_dir)
        traverse_q.append(next_isect)

  # graph.makePerimeterDirectional()
  # graph.writeGraphViz('day23b.gv')

  # print(f'entry {graph.edges[0].length}, exit {graph.edges[1].length}')
        
  return graph


class TraverseData:
  def __init__(self, graph, end_vertex):
    self.graph = graph
    self.end_vertex = end_vertex
    self.max_length = 0
    self.start_time = time.time()
    self.paths_found = 0

    # I don't understand--using this rather than vertex.visited flags seems
    # like it should be a small speed improvement, but it doubles the runtime
    # with cpython and has no measurable effect with pypy.
    self.visited_bitmask = 0


def findLongestPath(graph):
  start_vertex = graph.vertex_list[0]
  end_vertex = graph.vertex_list[1]
  start_vertex.visited = True
  trav = TraverseData(graph, end_vertex)
  # trav.visited_bitmask |= start_vertex.index

  length = graph.entry_edge_len + graph.exit_edge_len
  timer = time.time()

  findLongestRecurse(trav, start_vertex, length, 0)
  # trav.visited_bitmask ^= start_vertex.index
  start_vertex.visited = False

  # print(f'traverse time {time.time() - trav.start_time:.3f} sec')
  # print(f'{trav.paths_found} paths found')
  # print(f'part2 {trav.max_length} {trav.pathStr(trav.max_path)}')

  # print(f'part2 {trav.max_length}')
  return trav.max_length


def findLongestRecurse(trav, vertex, length, depth):
  # assert not vertex.visited

  # vertex = trav.path[-1]
  # print(f'{"  " * depth} fh {vertex}')
  
  if vertex == trav.end_vertex:
    # print(f'path length {length} found')
    # print(f'{length} path {trav.pathStr(trav.path)}')
    trav.paths_found += 1
    if length > trav.max_length:
      trav.max_length = length
      # trav.max_path = trav.path.copy()
      # print(f'{time.time() - trav.start_time:.3f} longest found {length}')
    return

  for next_vertex, next_length in vertex.peers:
    # if not trav.visited_bitmask & next_vertex.index:
    if not next_vertex.visited:
      # trav.visited_bitmask |= next_vertex.index
      next_vertex.visited = True
      findLongestRecurse(trav, next_vertex, length + next_length + 1, depth + 1)
      # trav.visited_bitmask ^= next_vertex.index
      next_vertex.visited = False


def findLongestPathNoRecursion(graph):
  """
  This is slower than the recursive solution with cpython, but is
  2x faster with pypy.
  """

  visited_bits = 0
  
  vertex = graph.vertex_list[0]
  end_vertex = graph.vertex_list[1]
  # vertex.visited = True
  visited_bits |= vertex.index
  start_time = time.time()
  max_length = 0
  paths_found = 0

  length = graph.entry_edge_len + graph.exit_edge_len
  timer = time.time()

  stack = []

  # len(vertex.peers) is really slow, so don't call it often
  peer_idx = len(vertex.peers) - 1

  while True:
    if peer_idx < 0:
      # vertex.visited = False
      visited_bits ^= vertex.index
      if stack:
        vertex, length, peer_idx = stack.pop()
        continue
      else:
        break

    next_vertex, edge_length = vertex.peers[peer_idx]
    next_length = length + edge_length + 1
    peer_idx -= 1

    if next_vertex == end_vertex:
      paths_found += 1
      # print(f'path length {next_length} found')
      if next_length > max_length:
        max_length = next_length
        # print(f'{time.time() - start_time:.3f} longest found {next_length}')
    else:
      # if not next_vertex.visited:
      if not visited_bits & next_vertex.index:
        stack.append((vertex, length, peer_idx))
        vertex = next_vertex
        # vertex.visited = True
        visited_bits |= next_vertex.index
        length = next_length
        peer_idx = len(vertex.peers) - 1
        
  # print(f'traverse time {time.time() - start_time:.3f} sec')

  return max_length



if __name__ == '__main__':
  filename = 'day23.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  timer = time.time()
  
  with open(filename) as inf:
    grid = readGrid(inf, True)

  graph = buildGraph(copy.deepcopy(grid))
  # length = findLongestPath(graph)
  length = findLongestPathNoRecursion(graph)
  print(f'part1 {length}')
  
  graph.makeAllEdgesBiDirectional()
  graph.makePerimeterDirectional()
  # graph.writeGraphViz('day23.gv')
  # length = findLongestPath(graph)
  length = findLongestPathNoRecursion(graph)
  print(f'part2 {length}')

  # print(f'timer {time.time() - timer:.3f}')
