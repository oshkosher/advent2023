#!/usr/bin/env python3

"""
Advent of Code 2023, day 13: Lens Library

Implement a hash table

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, re

"""
Determine the ASCII code for the current character of the string.
Increase the current value by the ASCII code you just determined.
Set the current value to itself multiplied by 17.
Set the current value to the remainder of dividing itself by 256.
After following these steps for each character in the string in order, the current value is the output of the HASH algorithm.
"""

def hashString(s):
  state = 0
  for c in s:
    state = ((state + ord(c)) * 17) & 255
  return state


def part1(filename):
  with open(filename) as inf:
    sum = 0
    for line in inf:
      words = line.split(',')
      for word in words:
        sum += hashString(word.strip())
  print(f'part1 {sum}')


cmd_re = re.compile(r'([a-z]+)(-|=)(\d*)')


def assignValue(value_list, key, value):
  """
  value_list one entry from table
  """
  for entry in value_list:
    if entry[0] == key:
      entry[1] = value
      return
  value_list.append([key, value])


def removeValue(value_list, key):
  """
  value_list one entry from table
  """
  for i in range(len(value_list)):
    if value_list[i][0] == key:
      del(value_list[i])
      return


def printTable(table):
  for i in range(len(table)):
    if not table[i]: continue
    sys.stdout.write(f'{i:3}:')
    for entry in table[i]:
      sys.stdout.write(f' {entry[0]}={entry[1]}')
    sys.stdout.write('\n')


def focusingPower(table):
  sum = 0
  for box_id in range(len(table)):
    box = table[box_id]
    for slot_id in range(1, len(box) + 1):
      slot = box[slot_id-1]
      sum += (box_id + 1) * slot_id * slot[1]
  return sum
    
def part2(filename):
  sum = 0

  # each entry in table is a list of [key, value] pairs
  table = [[] for _ in range(256)]

  with open(filename) as inf:
    for line in inf:
      cmds = line.split(',')
      for cmd in cmds:
        # print(cmd)
        m = cmd_re.match(cmd)
        if not m:
          print('Unrecognized command: ' + cmd)
          sys.exit(1)
        key = m.group(1)
        slot = hashString(key)
        op = m.group(2)
        if op == '=':
          value = int(m.group(3))
          assignValue(table[slot], key, value)
        elif op == '-':
          removeValue(table[slot], key)
        else:
          print(f'invalid op "{op}"')
          sys.exit(1)

        # printTable(table)
  print(f'part2 {focusingPower(table)}')


if __name__ == '__main__':
  filename = 'day15.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)

