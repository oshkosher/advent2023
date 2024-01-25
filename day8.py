#!/usr/bin/env python3

"""
Advent of Code 2023, day 8: Haunted Wasteland

Find the least common multiple of a set of cycles.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""


import sys, re, math

node_re = re.compile(r'([A-Z]+) = \(([A-Z]+), ([A-Z]+)\)')

class Node:
  def __init__(self, name, left = None, right = None):
    self.name = name
    self.left = left
    self.right = right

  def __str__(self):
    return self.name

def makeNode(name, d):
  if name in d:
    return d[name]
  else:
    n = Node(name)
    d[name] = n
    return n

def readInput(inf):
  # name -> Node
  nodes = {}

  turns = inf.readline().strip()
  inf.readline()
  for line in inf:
    match = node_re.search(line)
    if not match:
      print('Input error: ' + line)
      return
    node = makeNode(match.group(1), nodes)
    left = makeNode(match.group(2), nodes)
    right = makeNode(match.group(3), nodes)

    node.left = left
    node.right = right

  return (nodes, turns)
  

def part1(filename):
  with open(filename) as inf:
    (nodes, turns) = readInput(inf)
  
  # print(repr(nodes))
  steps = 0
  node = nodes['AAA']
  turn_pos = 0
  # print('AAA')
  while node.name != 'ZZZ':
    turn = turns[turn_pos]
    turn_pos += 1
    if turn_pos == len(turns):
      turn_pos = 0

    if turn == 'L':
      node = node.left
    else:
      assert turn == 'R'
      node = node.right
    steps += 1
    
    # print(f'{steps}. {node.name}')
  print(f'part1 {steps}')


def isStartNode(node):
  return node.name[2] == 'A';

def isEndNode(node):
  return node.name[2] == 'Z';

def turnGenerator(turns):
  turn_pos = 0
  while True:
    yield turns[turn_pos]
    turn_pos += 1
    if turn_pos == len(turns):
      turn_pos = 0


class Path:
  def __init__(self, start_node):
    self.start_node = start_node

    # list of (steps, end_node) tuples
    self.cycle_list = []

  def findCycles(self, nodes, turns):
    n = self.start_node;
    end_nodes = set()

    steps = 0
    turn_gen = turnGenerator(turns)
    while True:
      if next(turn_gen) == 'L':
        n = n.left
      else:
        n = n.right
      steps += 1

      if isEndNode(n):
        self.cycle_list.append((steps, n))
        if n in end_nodes:
          return
        end_nodes.add(n)
        steps = 0

  def __str__(self):
    return ' '.join([f'({str(s[0])}, {s[1].name})' for s in self.cycle_list])


def part2(filename):
  with open(filename) as inf:
    (nodes, turns) = readInput(inf)

  cycle_lengths = []

  for node in nodes.values():
    if not isStartNode(node): continue
    path = Path(node)
    path.findCycles(nodes, turns)
    # print(f'{node.name} path: {path}')
    cycle_len = path.cycle_list[0][0]
    cycle_lengths.append(cycle_len)
  lcm = math.lcm(*cycle_lengths)
  print(f'part2 {lcm}')
    
  
if __name__ == '__main__':
  filename = 'day8.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
