#!/usr/bin/env python3

"""
Advent of Code 2023, day 5: If You Give A Seed A Fertilizer

Subrange splitting and remapping.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, bisect

class Mapping:
  def __init__(self, name):
    self.name = name

    # ordered list of src_start
    self.key_list = []
    
    # ordered list of (src_start, dest_start, length) tuples
    self.mapping_list = []

  def add(self, src_start, dest_start, length):
    self.mapping_list.append((src_start, dest_start, length))

  def compile(self):
    self.mapping_list.sort()
    self.key_list = [entry[0] for entry in self.mapping_list]

  def print(self, title):
    print(f'Mapping {title}:')
    for src_start, dest_start, length in self.mapping_list:
      print(f'  {src_start:,} - {src_start + length:,}:  {dest_start - src_start:+}')

  def isValid(self):
    # check that the mapping_list is ordered and nonoverlapping, and that
    # it aligns with key_list
    if len(self.key_list) != len(self.mapping_list): return False

    for i in range(len(self.key_list)):
      m = self.mapping_list[i]
      if self.key_list[i] != m[0]: return False
      if i > 0:
        prev = self.mapping_list[i-1]
        if m[0] < prev[0] + prev[2]: return False
    return True

  def search(self, point):
    """
    If the given point is within the range of a mapping, return the index
    of that mapping. Otherwise return -1.
    """
    for i, m in enumerate(self.mapping_list):
      if point >= m[0] and point < m[0] + m[2]:
        return i
    return -1

  def lookup(self, key):
    """
    Look for the first entry with entry_key <= key.
    If the given key falls in the range for that entry, return
    the destination value. Otherwise return key.
    """

    # bisect_right does a binary search and will return the entry after
    # the one we want.
    # key[:i+1] are all <= key
    i = bisect.bisect_right(self.key_list, key)

    # print(f'lookup key {key}: i={i}')
    if i == 0: return key
    # (src_start, dest_start, length)
    mapping = self.mapping_list[i-1]
    # print(f'  lookup mapping {mapping!r}, offset={key - mapping[0]}')
    assert key >= mapping[0]
    if key - mapping[0] >= mapping[2]:
      return key
    else:
      return mapping[1] + key - mapping[0]


class RangeList:
  def __init__(self):
    self.range_list = []

  def add(self, start, length):
    self.range_list.append([start, length])

  def size(self):
    return sum([r[1] for r in self.range_list])

  def isValid(self):
    for i in range(1, len(self.range_list)):
      r = self.range_list[i]
      prev = self.range_list[i-1]
      if r[0] < prev[0] + prev[1]: return False
    return True

  def search(self, point):
    """
    If the given point is within one of the ranges, return the index
    of that range. Otherwise return -1.
    """
    for i, r in enumerate(self.range_list):
      if point >= r[0] and point < r[0] + r[1]:
        return i
    return -1
    
  
  def compile(self):
    """
    Put all the ranges in order and coalesce overlaps.
    """
    self.range_list.sort()
    i = 0
    while i < len(self.range_list) - 1:
      r = self.range_list[i]
      next = self.range_list[i+1]

      # check that the list is ordered
      assert r[0] <= next[0]

      # n overlap
      if r[0] + r[1] < next[0]:
        i += 1
        continue

      # compile r and next
      end = max(r[0] + r[1], next[0] + next[1])
      r[1] = end - r[0]
      del(self.range_list[i+1])

  def print(self, title):
    print('RangeList ' + title)
    for (start, length) in self.range_list:
      print(f'  {start:,} .. {start+length:,}')
      

def readInput(inf):
  line = inf.readline()
  assert line.startswith('seeds: ')
  seed_list = [int(x) for x in line[7:].split()]

  mapping_list = []

  inf.readline()
  assert inf.readline().startswith('seed-to-soil map:')
  mapping_list.append(readMap(inf, 'seed-to-soil'))

  assert inf.readline().startswith('soil-to-fertilizer map:')
  mapping_list.append(readMap(inf, 'soil-to-fertilizer'))

  assert inf.readline().startswith('fertilizer-to-water map:')
  mapping_list.append(readMap(inf, 'fertilizer-to-water'))

  assert inf.readline().startswith('water-to-light map:')
  mapping_list.append(readMap(inf, 'water-to-light'))

  assert inf.readline().startswith('light-to-temperature map:')
  mapping_list.append(readMap(inf, 'light-to-temperature'))

  assert inf.readline().startswith('temperature-to-humidity map:')
  mapping_list.append(readMap(inf, 'temperature-to-humidity'))

  assert inf.readline().startswith('humidity-to-location map:')
  mapping_list.append(readMap(inf, 'humidity-to-location'))

  return (seed_list, mapping_list)


def readMap(inf, name):
  mapping = Mapping(name)
  while True:
    line = inf.readline()
    if len(line)==0 or line[0] == '\n':
      break

    (dest_start, src_start, length) = [int(x) for x in line.split()]
    mapping.add(src_start, dest_start, length)

  mapping.compile()

  # print(f'{name}')
  # print(f'  {mapping.key_list!r}')
  # for (src_start, dest_start, length) in mapping.mapping_list:
  #   print(f'  {src_start}:{src_start+length-1} -> {dest_start}:{dest_start+length-1}')
  
  return mapping


def seedToLocation(seed, mapping_list):
  i = seed
  for mapping in mapping_list:
    i = mapping.lookup(i)
  return i


def remapRangeList2(range_list, mapping):
  """
  do a kind of merge on the range list and mapping list
  """
  output_range_list = RangeList()
  input_range_list = range_list.range_list
  mapping_list = mapping.mapping_list

  # first check that the list of ranges are ordered and non-overlapping
  assert range_list.isValid()
  assert mapping.isValid()
  
  # collect all the start/end point from either set of ranges
  points = set()
  for r in input_range_list:
    points.add(r[0])
    points.add(r[0] + r[1])
  for m in mapping_list:
    points.add(m[0])
    points.add(m[0] + m[2])

  points = list(points)
  points.sort()
  # print(f'points: {points}')

  for i in range(1, len(points)):
    start = points[i-1]
    length = points[i] - start
    ri = range_list.search(start)
    # ignore anything that isn't in the input range
    if ri != -1:
      mi = mapping.search(start)
      if mi != -1:
        # remapped subrange
        m = mapping_list[mi]
        offset = m[1] - m[0]
        output_range_list.add(start + offset, length)
      else:
        output_range_list.add(start, length)
  
  output_range_list.compile()
  return output_range_list

    
def part1(seed_list, mapping_list):
  min_location = None
  for seed in seed_list:
    location = seedToLocation(seed, mapping_list)
    if min_location == None or location < min_location:
      min_location = location

  print(f'part1 {min_location}')


def part2(seed_list, mapping_list):
  min_location = None
  ranges = RangeList()
  for i in range(0, len(seed_list), 2):
    start = seed_list[i]
    length = seed_list[i+1]
    ranges.add(start, length)
    # print(f'seeds {start_seed_idx} .. {start_seed_idx+length}')
  ranges.compile()
  # ranges.print(f'Seeds size={ranges.size()}')

  for mi, m in enumerate(mapping_list):
    ranges = remapRangeList2(ranges, m)
    # ranges.print(f'ranges after map {mi}, size={ranges.size()}')
  
  print(f'part2 {ranges.range_list[0][0]}')


if __name__ == '__main__':
  filename = 'day5.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]

  with open(filename) as inf:
    (seed_list, mapping_list) = readInput(inf)
    
  part1(seed_list, mapping_list)

  part2(seed_list, mapping_list)
  

