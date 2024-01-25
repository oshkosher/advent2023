#!/usr/bin/env python

"""
Advent of Code 2023, day 2: Cube Conundrum

Applying min/max constraints.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, re


line_re = re.compile(r'Game (\d+): (.*) *')
color_count_re = re.compile(f'(\d+) (red|green|blue)')

# max_red = 12
# max_green = 13
# max_blue = 14

part1_max = {
  'red': 12,
  'green': 13,
  'blue': 14,
  }


def parseResult(result_str):
  """
  given a result such as "8 green, 6 blue, 20 red"
  return it as a list of tuples:
    [('green', 8), ('blue', 6), ('red', 20)]
  """
  color_list = []
  for color_count in [x.strip() for x in result_str.split(',')]:
    match = color_count_re.match(color_count)
    if not match:
      print(f'Unrecognized color count string: {repr(color_count)}')
      sys.exit(1)
    count = int(match.group(1))
    color = match.group(2)
    color_list.append((color, count))
  return color_list


def isResultPossible(results):
  # results is a list of (color, count) tuples
  for color, count in results:
    if count > part1_max[color]:
      return False
  return True


def part1(filename):
  game_num_sum = 0

  with open(filename) as inf:
    for line in inf:
      m = line_re.match(line)
      game_no = int(m.group(1))
      result_list = [x.strip() for x in m.group(2).split(';')]

      all_possible = True
      for results in [parseResult(r) for r in result_list]:
        if not isResultPossible(results):
          all_possible = False
          break

      if all_possible:
        game_num_sum += game_no
      # print(f'Game {game_no} possible: {all_possible}')

  print(f'part1 {game_num_sum}')


def part2(filename):
  game_sum = 0

  with open(filename) as inf:
    
    for line in inf:
      color_max = {'red': 0, 'blue': 0, 'green': 0}
      m = line_re.match(line)
      game_no = int(m.group(1))
      result_list = [x.strip() for x in m.group(2).split(';')]
      for results in [parseResult(r) for r in result_list]:
        for color, count in results:
          color_max[color] = max(color_max[color], count)
      power = color_max['red'] * color_max['blue'] * color_max['green']
      # print(f'game {game_no} red {color_max["red"]}, green {color_max["green"]}, blue {color_max["blue"]}, power {power}')
      game_sum += power
      

  print(f'part2 {game_sum}')


if __name__ == '__main__':
  filename = 'day2.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
