#!/usr/bin/env python3

"""
Advent of Code 2023, day 12: Hot Springs

Pattern matching, combinatorials, dynamic programming.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys

def readInput(inf):
  # (str, [pattern, ...])
  inputs = []
  for line in inf:
    s, p = line.split()
    s = [c for c in s]
    p = [int(i) for i in p.split(',')]
    inputs.append((s,p))
  return inputs

def matches(s, p):
  i = 0
  while i < len(s) and s[i] == '.':
    i += 1
  if len(p) == 0:
    return int(i == len(s))
  
  for j in range(p[0]):
    if i >= len(s) or s[i] != '#': return 0
    i += 1

  for length in p[1:]:
    if i >= len(s) or s[i] != '.': return 0
    while i < len(s) and s[i] == '.':
      i += 1
    
    for j in range(length):
      if i >= len(s) or s[i] != '#': return 0
      i += 1

  while i < len(s):
    if s[i] != '.': return 0
    i += 1

  # print(f'  {"".join(s)} == {p}')
  return 1


def countOptionsSlow(string, pattern, pos):
  while pos < len(string) and string[pos] != '?':
    pos += 1
  if pos == len(string):
    return matches(string, pattern)
  
  string[pos] = '.'
  c = countOptionsSlow(string, pattern, pos)
  string[pos] = '#'
  c += countOptionsSlow(string, pattern, pos)
  string[pos] = '?'
  return c
  

def part1(inputs):
  # inputs = readInput(inf)
  sum = 0
  for string, pattern in inputs:
    # print(f'{"".join(string)} == {pattern}')
    # count = countOptionsSlow(string, pattern, 0)
    count = countOptionsFast(string, pattern)
    # print(f'  {count}')
    sum += count
  print(f'part1 {sum}')


def expandString(s):
  s2 = s.copy()
  for _ in range(4):
    s2.append('?')
    s2.extend(s)
  return s2

def expandPattern(p):
  p2 = p+p
  return p2+p2+p

def linearizePattern(p):
  """
  Expand each part of a pattern and put dots between each.
  Forn example: [1,2,3] -> "#.##.###"
  """
  return '.'.join(['#'*x for x in p])

def linearizePattern2(p):
  """
  Expand each part of a pattern and put dots before, after, and between each.
  Forn example: [1,2,3] -> ".#.##.###."
  """
  return '.' + '.'.join(['#'*x for x in p]) + '.'

def linearizedPatternLen(p):
  return 1 + len(p) + sum(p)


def addOption2(opt, pi, prefixes, suffix):
  prefixes = [p+suffix for p in prefixes]
  l = opt.get(pi, None)
  if l:
    l.extend(prefixes)
  else:
    opt[pi] = prefixes
    

def addOption(opt, pi, count):
  prev_count = opt.get(pi, 0)
  opt[pi] = prev_count + count


def countOptionsFast(string, pattern):
  """
  Track every possible route to a solution, collapsing paths that achieve
  the same amount of progress.
  """
  pattern = linearizePattern(pattern)
  # print(f'{"".join(string)} == {pattern}')
  # position_in_pattern -> count
  opt = {0: 1}
  prev_opt = {}

  for si, s in enumerate(string):
    tmp = prev_opt
    prev_opt = opt
    opt = tmp
    opt.clear()

    # print(f'  {si} {s}')
    
    if s == '#':
      for pi, count in prev_opt.items():
        if pi < len(pattern) and pattern[pi] == '#':
          addOption(opt, pi+1, count)
          # anything other than # is a mismatch  
        
    elif s == '.':
      for pi, count in prev_opt.items():
        if pi >= len(pattern) or pi == 0 or (pattern[pi] == '#' and pattern[pi-1] == '.'):
          addOption(opt, pi, count)
        elif pattern[pi] == '.':
          addOption(opt, pi+1, count)
          
    else:
      assert s == '?'
      for pi, count in prev_opt.items():
        if pi >= len(pattern):
          # must be considered a .
          addOption(opt, pi, count)
        elif pattern[pi] == '.':
          # must be considered a .
          addOption(opt, pi+1, count)
        else:
          assert pattern[pi] == '#'
          addOption(opt, pi+1, count)
          if pi==0 or pattern[pi-1] == '.':
            addOption(opt, pi, count)
          
    # for pi, prefixes in opt.items():
    #   print(f'    {pi}({len(prefixes)}) {" ".join(prefixes)}')

  count = opt.get(len(pattern), 0)
  return count
        
          
def part2(inputs):
  #  .??..??...?##.?.??..??...?##.?.??..??...?##.?.??..??...?##.?.??..??...?##.
  # [1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3, 1, 1, 3]
  """
  reduce all repeated '.' to a single
  .#####. is an exact match in pattern
  .##????. or .???###. matches a range of values
  ###??### can be split or joined

  p: 1,1,3 --> #.#.###
  s: ???.###

  leading dots: anything before the first #
   ?  if . then still at 0, if # then move to 1
   ?  (0,.): 0, (0,#): 1, (1,#): no, (1,.): 2
   ?  (0,.): 0, (0,#): 1, (1,#): no, (1,.): 2, (2,.): 2, (2,#): 3
   .  0: 0, 1: 2, 2: 2, 3: 4
   #  0: 1, 1: no, 2: 3, 3: no, 4: 5
   #  1: no, 3: no, 5: 6
   #  6: 7

  p:  #.#.###
  s: .??..??...?##.
   . 0: 0
   ? 0.: 0, 0#: 1
   ? 0.: 0, 0#: 1, 1.: 2, 1#: no
     (0 ..., 1 ..#, 2 .#.)
   . 0[1], 2[2]  (0 ...., 2 .#.., 2 ..#.)
     0: 0.
     1:
     2: 1., 2.
     3: 
   .
   ?
   ?
   .
   .
   .
   ?
   #
   #
   .
  
  """
  sum = 0
  for string, pattern in inputs:

    string = expandString(string)
    pattern = expandPattern(pattern)
    count = countOptionsFast(string, pattern)
    # print(f'  {count}\n')
    sum += count
  print(f'part2 {sum}')


if __name__ == '__main__':
  filename = 'day12.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  with open(filename) as inf:
    inputs = readInput(inf)
  part1(inputs)
  part2(inputs)
