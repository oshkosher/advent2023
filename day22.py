#!/usr/bin/env python3

"""
Advent of Code 2023, day 22: Sand Slabs

Jenga and dependency graphs

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, re, collections, time

brick_re = re.compile(r'(\d+),(\d+),(\d+)~(\d+),(\d+),(\d+)')


AXIS_X = 0
AXIS_Y = 1
AXIS_Z = 2


def minFirst(a, b):
  return (a,b) if a <= b else (b,a)


class Node:
  def __init__(self, brick):
    self.brick = brick
    self.in_nodes = set()
    self.out_nodes = set()

    # number of nodes that would fall if this node was removed, including
    # this one
    self.fall_size = None

  def __str__(self):
    return str(self.brick.index)

  def __eq__(self, that):
    return self.brick is that.brick

  def __hash__(self):
    return hash(self.brick)

  def __lt__(self, that):
    return self.brick.index < that.brick.index


class Brick:
  def __init__(self, index, line):
    self.index = index
    m = brick_re.search(line)
    if not m:
      print('Bad input line: ' + line)
      return
    x1,y1,z1,x2,y2,z2 = (
      int(m.group(i))
      for i in range(1, 7)
    )

    self.coords = [minFirst(x1,x2), minFirst(y1,y2), list(minFirst(z1,z2))]

    # set the axis of this brick to the dimension that is > 1.
    # If it's 1x1x1, let X be the axis.
    self.axis = -1
    for ax in range(1, len(self.coords)):
      c = self.coords[ax]
      assert c[0] <= c[1]
      if c[0] < c[1]:
        if self.axis > -1:
          assert False, f'Brick {self.index} invalid shape {line}'
        self.axis = ax
    if self.axis == -1:
      self.axis = AXIS_X


    c = self.coords[self.axis]
    self.length = c[1] - c[0] + 1

    # ((x1, x2), (y1,y2), (z1, z2))
    # self.coords

    # print(f'create brick {index} {self}')

      
  def __lt__(self, that):
    return self.bottom() < that.bottom()


  @staticmethod
  def rangeStr(a, b):
    if a == b:
      return str(a)
    else:
      return str(a) + '-' + str(b)
    

  def __str__(self):
    return f'Brick({self.index}, x={Brick.rangeStr(*self.coords[0])}, y={Brick.rangeStr(*self.coords[1])}, z={Brick.rangeStr(*self.coords[2])})'

  
  def bottom(self):
    """
    z-coordinate of lowest cube in this brick
    """
    return self.coords[AXIS_Z][0]

  
  def top(self):
    """
    z-coordinate of highest cube in this brick
    """
    return self.coords[AXIS_Z][1]
  

  def verticalRangeStr(self):
    if self.top() > self.bottom():
      return f'{self.index}({self.bottom()}-{self.top()})'
    else:
      return f'{self.index}({self.bottom()})'

  
  def fall(self, dist):
    """
    Lower my height by this much.
    """
    z = self.coords[AXIS_Z]
    z[0] -= dist
    z[1] -= dist
      

  def bases(self):
    """
    Generator for all the cubes at the lowest level of this brick.
    For bricks with orientation X or Y, this will yield self.length cubes.
    If orientation Z, this will return a single cube.
    For each cube an (x,y,z) coordinate will be returned.
    """
    c = [x[0] for x in self.coords]
    if self.axis == AXIS_Z:
      yield c
    else:
      for i in range(self.length):
        yield c
        c[self.axis] += 1


  def contains(self, coord1):
    """
    Returns true if this brick contains this coordinate.
    """
    for c, rng in zip(coord1, self.coords):
      if c < rng[0] or c > rng[1]:
        return False
    return True

  
  def intersects(self, that):
    """
    Returns True iff self and that overlap.
    It's sufficient if our bounds overlap in every dimension.
    """
    for c1,c2 in zip(self.coords, that.coords):
      if c1[1] < c2[0] or c1[0] > c2[1]:
        return False
    return True

  
  def intersectsXY(self, that):
    """
    Returns True iff self and that would overlap if self.bottom()==that.bottom().
    It's sufficient if our bounds overlap in every dimension.
    """
    for c1,c2 in zip(self.coords[:2], that.coords[:2]):
      if c1[1] < c2[0] or c1[0] > c2[1]:
        return False
    return True


class Tower:
  def __init__(self, bricks):
    # make a copy of the array of bricks and sort by bottom()
    self.bricks = bricks[:]
    self.bricks.sort()

    self.sizes = Tower.findSize(self.bricks)

    # 3-d list
    # stacks[x][y] is a list of bricks stacked in that cell, with the
    # lowest ones (lowest Z value) first.
    self.stacks = [[[] for _ in range(self.sizes[1])] for _ in range(self.sizes[0])]

    for b in self.bricks:
      if b.axis == AXIS_Z:
        x = b.coords[0][0]
        y = b.coords[1][0]
        self.stacks[x][y].append((b.bottom(), b))
      else:
        for (x,y,z) in b.bases():
          self.stacks[x][y].append((z, b))


    # order by z-coordinate in each stack and replace each tuple with
    # just the brick reference
    for row in self.stacks:
      for stack in row:
        stack.sort()
        for i in range(len(stack)):
          stack[i] = stack[i][1]

  @staticmethod
  def findSize(bricks):
    maxes = [0, 0, 0]

    for b in bricks:
      for i in range(3):
        maxes[i] = max(maxes[i], b.coords[i][1])

    return tuple(x+1 for x in maxes)


  def droppableDistance(self, brick):
    """
    Returns distance this brick can be lowered without changing z-ordering,
    and with a minimum z-value of 1.
    """
    min_fall = None
    for (x,y,z) in brick.bases():
      stack = self.stacks[x][y]
      i = stack.index(brick)
      if i == 0:
        fall = brick.bottom() - 1
      else:
        fall = brick.bottom() - stack[i-1].top() - 1
      if min_fall == None or fall < min_fall:
        min_fall = fall
      
    return min_fall
    
  
    
  def dropAll(self):
    """
    Let all bricks fall until they can fall no more.
    """

    still_falling = True
    release_iter = 0
    while still_falling:
      release_iter += 1
      # print(f'release iter {release_iter}')

      still_falling = False
      for b in self.bricks:
        dist = self.droppableDistance(b) 
        # dist2 = self.droppableDistanceSlow(b)
        # if dist != dist2:
        #   print(f'brick {b.index} fast dist {dist}, slow dist {dist2}')
        if dist > 0:
          still_falling = True
          self.drop(b, dist)
          # print(f'Drop {b.index} by {dist}: {b}')
    

  def drop(self, brick, dist):
    if dist <= 0: return
    brick.coords[2][0] -= dist
    brick.coords[2][1] -= dist


  def listSupporters(self, brick):
    """
    Returns a list of the indices of the bricks supporting this brick.
    Those are the ones just below me in the cell stack with top() 1 less
    than my bottom().
    """
    supporters = set()
    for (x,y,z) in brick.bases():
      stack = self.stacks[x][y]
      i = stack.index(brick)
      if i == 0:
        # at the bottom; no support needed
        continue
      below = stack[i-1]
      if below.top() == brick.bottom() - 1:
        supporters.add(below)

    # can a node be listed multiple times a a supporter??
    
    return supporters


  def countRemovableBricks(self):
    essential_brick_ids = set()

    for b in self.bricks:
      # for each brick, make a list of the bricks supporting it
      supporters = self.listSupporters(b)
      
      # sups = ' '.join([str(x) for x in supporters])
      # print(f'supporters of {b.index}: {sups}')

      # if there is a single brick supporting it, add that brick
      # to the essential set
      if len(supporters) == 1:
        for s in supporters:
          essential_brick_ids.add(s)

    # esses = ' '.join([str(x) for x in essential_brick_ids])
    # print(f'essentials: {esses}')

    # count non-essential bricks
    return len(self.bricks) - len(essential_brick_ids)


  def buildSupportGraph(self):
    """
    Build a graph of which bricks support which.
    It will be a DAG.
    Returns a list of Node objects.
    """
    node_list = []
    bricks_to_nodes = {}
    for brick in self.bricks:
      node = Node(brick)
      node_list.append(node)
      bricks_to_nodes[brick] = node

    for node in node_list:
      # print(f'supporters of {node}')
      sups = self.listSupporters(node.brick)
      # print(' '.join([str(x) for x in sups]))
      for sup in sups:
        sup_node = bricks_to_nodes[sup]
        sup_node.out_nodes.add(node)
        node.in_nodes.add(sup_node)

    return node_list


  def computeFallSizesAll(self, node_list):
    """
    Set fall_size attribute for each node in node_list.

    If a node has no out_nodes then its fall_size is 1.

    If it does have out_nodes, then traverse them in BFS order, computing
    whether they will fall if this node and its dependents fall.
    Maintain a set, initially only containing the initial node, of nodes
    that have fallen. For each node that is traversed, if all the nodes
    in its in_nodes have fallen then add it to the fallen set. 
    """

    for node in node_list:
      node.fall_size = self.computeFallSize(node)
      

  def computeFallSize(self, root_node):
    fallen_nodes = set()
    traverse_q = collections.deque()
    fallen_nodes.add(root_node)
    traverse_q.append(root_node)
    while len(traverse_q) > 0:
      tv_node = traverse_q.popleft()
      for out_node in tv_node.out_nodes:
        # all of the supports for this brick have fallen, so it will fall
        if out_node.in_nodes <= fallen_nodes:
          fallen_nodes.add(out_node)
          traverse_q.append(out_node)
        
    result = len(fallen_nodes) - 1
    # print(f'Fall set if {root_node} is removed: {" ".join([str(x) for x in fallen_nodes])}')
    return result
      

def readInput(inf):
  bricks = []
  for line in inf:
    i = len(bricks)
    bricks.append(Brick(i, line))

  return bricks
 

def part1(filename):
  with open(filename) as inf:
    bricks = readInput(inf)
  # print(f'{len(bricks)} bricks created')
  tower = Tower(bricks)

  tower.dropAll()

  n_removable = tower.countRemovableBricks()
  print(f'part1 {n_removable}')


def part2(filename):
  with open(filename) as inf:
    bricks = readInput(inf)
  # print(f'{len(bricks)} bricks created')
  tower = Tower(bricks)

  tower.dropAll()

  graph = tower.buildSupportGraph()

  fall_size_sum = 0
  tower.computeFallSizesAll(graph)
  for node in graph:
    fall_size_sum += node.fall_size
    # print(f'Brick {node.brick.index} fall size {node.fall_size}')

  print(f'part2 {fall_size_sum}')
  

if __name__ == '__main__':
  filename = 'day22.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  timer = time.time()
  part1(filename)
  part2(filename)
  timer = time.time() - timer
  # print(f'timer {timer:.3f}')
