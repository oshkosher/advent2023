#!/usr/bin/env python

"""
Advent of Code 2023, day 1: Trebuchet?!

Parsing digits or digit names from a string.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, re

digit_re = re.compile(r'(\d|one|two|three|four|five|six|seven|eight|nine)')

digit_from_string = {
  '1': 1,
  'one': 1,
  '2': 2,
  'two': 2,
  '3': 3,
  'three': 3,
  '4': 4,
  'four': 4,
  '5': 5,
  'five': 5,
  '6': 6,
  'six': 6,
  '7': 7,
  'seven': 7,
  '8': 8,
  'eight': 8,
  '9': 9,
  'nine': 9
  }


def findAllOverlapping(regexp, s):
  result = []
  pos = 0
  while True:
    match = regexp.search(s[pos:])
    if not match:
      break
    # print(f'found "{match.group(0)}" at {pos + match.start(0)}')
    result.append(match.group(0))
    pos = pos + match.start(0) + 1
  return result


def lineValue(s):
  
  digit_strings = findAllOverlapping(digit_re, s)
  if not digit_strings:
    print(f'Error: line contains no digits: {s}')
    sys.exit(1)

  first = digit_from_string[digit_strings[0]]
  last = digit_from_string[digit_strings[-1]]

  value = first * 10 + last
  # print(f'{s}: {value}')
  return value


def part1(filename):
  digit_re = re.compile(r'(\d)')
  sum = 0
  with open(filename) as inf:
    for line in inf:
      digit_strings = re.findall(digit_re, line)
      value = int(digit_strings[0]) * 10 + int(digit_strings[-1])
      sum += value
      # print(f'{value}: {line.strip()}')
  print(f'part1: {sum}')
  

def part2(filename):
  sum = 0
  with open(filename) as inf:
    for line in inf:
      value = lineValue(line)
      sum += value
      # print(f'{value}: {line.strip()}')
  print(f'part2: {sum}')


if __name__ == '__main__':
  filename = 'day1.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)

