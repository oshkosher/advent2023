#!/usr/bin/env python

import sys, re


line_re = re.compile(r'Game (\d+): (.*) *')
color_count_re = re.compile(f'(\d+) (red|green|blue)')

max_red = 12
max_green = 13
max_blue = 14


def isResultPossible(result):
  color_counts = [x.strip() for x in result.split(',')]
  for color_count in color_counts:
    m = color_count_re.match(color_count)
    if not m:
      print(f'Unrecognized color count string: {repr(color_count)}')
      sys.exit(1)
    count = int(m.group(1))
    color = m.group(2)
    if color == 'red' and count > max_red: return False
    if color == 'blue' and count > max_blue: return False
    if color == 'green' and count > max_green: return False
  return True

game_num_sum = 0

class ColorSet:
  def __init__(self):
    self.red = 0
    self.green = 0
    self.blue = 0

  # track the maximum value given for each color
  def add(self, color, value):
    if color == 'red':
      self.red = max(self.red, value)
    elif color == 'green':
      self.green = max(self.green, value)
    elif color == 'blue':
      self.blue = max(self.blue, value)
    else:
      print('unrecognized color ' + color)
      sys.exit(1)

      
sum = 0

for line in sys.stdin:
  color_set = ColorSet()

  m = line_re.match(line)
  game_no = int(m.group(1))
  result_list = [x.strip() for x in m.group(2).split(';')]
  # print(f'game {game_no}: {repr(result_list)}')

  for result in result_list:
    color_counts = [x.strip() for x in result.split(',')]
    for color_count in color_counts:
      m = color_count_re.match(color_count)
      if not m:
        print(f'Unrecognized color count string: {repr(color_count)}')
        sys.exit(1)
      count = int(m.group(1))
      color = m.group(2)
      color_set.add(color, count)

  print(f'Game {game_no}: red {color_set.red}, blue {color_set.blue}, green {color_set.green}')
  
  sum += color_set.red * color_set.blue * color_set.green

print(f'sum = {sum}')

