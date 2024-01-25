#!/usr/bin/env python3

"""
Advent of Code 2023, day 9: Mirage Maintenance

Polynomial extrapolation

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys


def allZero(row):
  for e in row:
    if e !=0: return False
  return True

def diffRow(row):
  return [row[i]-row[i-1] for i in range(1,len(row))]

def rowStr(row):
  return ' '.join([str(x) for x in row])

def part1(inf):
  with open(filename) as inf:
    exsum = 0
    for line in inf:
      rows = []
      rows.append([int(x) for x in line.split()])
      # print(rowStr(rows[-1]))

      while len(rows[-1]) > 1 and not allZero(rows[-1]):
        rows.append(diffRow(rows[-1]))
        # print(rowStr(rows[-1]))

      if len(rows[-1]) == 1 and rows[-1][0] != 0:
        print('Didnt resolve')
        continue

      for i in range(len(rows)-2, -1, -1):
        rows[i].append(rows[i][-1] + rows[i+1][-1])

      #for row in rows:
      #  print(rowStr(row))
      #print()
      exsum += rows[0][-1]

  print(f'part1 {exsum}')


def part2(filename):
  with open(filename) as inf:
    exsum = 0
    for line in inf:
      rows = []
      rows.append([int(x) for x in line.split()])
      # print(rowStr(rows[-1]))

      while len(rows[-1]) > 1 and not allZero(rows[-1]):
        rows.append(diffRow(rows[-1]))
        # print(rowStr(rows[-1]))

      if len(rows[-1]) == 1 and rows[-1][0] != 0:
        print('Didnt resolve')
        continue

      for i in range(len(rows)-2, -1, -1):
        rows[i][0:0] = [rows[i][0] - rows[i+1][0]]

      # for row in rows:
      #   print(rowStr(row))
      # print()
      exsum += rows[0][0]

  print(f'part2 {exsum}')


if __name__ == '__main__':
  filename = 'day9.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
