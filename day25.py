#!/usr/bin/env python3

"""
Advent of Code 2023, day 25: Snowverload

Graph min-cut.

I took another easy way out on this one.
I just output the graph in graphviz format, then visually noted
which three edges connected the two dense subgraphs.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, collections


class Connectivity:
  def __init__(self, rules):
    # name -> peer_list
    self.nodes = {}
    
    for src, dests in rules:
      for dest in dests:
        self.add(src, dest)

  def add(self, n1, n2):
    self.addOne(n1, n2)
    self.addOne(n2, n1)

  def addOne(self, a, b):
    peers = self.nodes.get(a, None)
    if peers == None:
      peers = [b]
      self.nodes[a] = peers
    else:
      if b not in peers:
        peers.append(b)

  def remove(self, n1, n2):
    self.nodes[n1].remove(n2)
    self.nodes[n2].remove(n1)

  def removeOne(self, a, b):
    self.nodes[a].remove(b)

  def countReachable(self, start):
    # count = 1
    visited = set()
    visited.add(start)
    q = collections.deque()
    q.append(start)

    while len(q) != 0:
      node = q.popleft()
      for peer in self.nodes[node]:
        if peer not in visited:
          visited.add(peer)
          q.append(peer)

    return len(visited)

  def write(self, filename):
    with open(filename, 'w') as outf:
      outf.write('graph day25 {\n')
      for src, dests in self.nodes.items():
        for dest in dests:
          if src < dest:
            outf.write(f'  {src} -- {dest}\n')
      outf.write('}\n')
    print(f'wrote {filename}')
    print(f'  neato -Tpdf -oday25.pdf {filename}')


def readInput(inf):
  """
  Returns [(name, [list of names]), ...]
  """
  rules = []
  for line in inf:
    colon = line.index(':')
    src = line[:colon]
    dests = line[colon+1:].split()
    rules.append((src, dests))
  return rules


def createConnectivityTable(rules):
  # enter every connection twice, for easy bidirectional access
  conn_dict = {}
  for src, dests in rules:
    for dest in dests:
      conn_dict[src] = dest
      conn_dict[dest] = src
  return conn_dict


def writeGraph(rules, filename):
  with open(filename, 'w') as outf:
    outf.write('graph day25 {\n')
    for src, dests in rules:
      for dest in dests:
        outf.write(f'  {src} -- {dest}\n')
    outf.write('}\n')
  print(f'wrote {filename}')
  print(f'  neato -Tpdf -oday25.pdf {filename}')

  
def part1(args):
  
  if len(args) < 1:
    print("""
  day25.py input foo-bar foo bar write:filename.gv
    Each x-y argument is a connection to be severed.
    Args which are node names start a reachability traversal.
    For each write arg write a graphviz file.
""")
    return
  

  with open(args[0]) as inf:
    con = Connectivity(readInput(inf))

  for arg in args[1:]:
    if arg.startswith('write:'):
      filename = arg[6:]
      con.write(filename)
      continue
    
    hyphen = arg.find('-')
    if hyphen != -1:
      n1,n2 = arg.split('-')
      # print(f'sever {n1} -- {n2}')
      con.remove(n1, n2)
      continue
    
    count = con.countReachable(arg)
    print(f'{count} reachable from {arg}')


# ./day25.py < day25.in.txt jpn vgf jpn-vgf nmz-mnl fdb-txm jpn vgf write:day25.cut3.gv

if __name__ == '__main__':
  args = sys.argv[1:]
  if len(args) == 0:
    args = ["day25.in.txt", 'jpn-vgf', 'nmz-mnl', 'fdb-txm', 'jpn', 'vgf']

  part1(args)
  
