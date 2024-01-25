#!/usr/bin/env python3

"""
Advent of Code 2023, day 4: Scratchcards

Computing subsets, summing stacked duplicates.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys, re, collections

line_re = re.compile(r'^Card *(\d+): ([0-9 ]*) \| ([0-9 ]*)')


def countWins(winning_num_list, card_num_list):
  winning_set = set()
  for value in [int(x) for x in winning_num_list.split()]:
    winning_set.add(value)
  
  match_count = 0
  for value in [int(x) for x in card_num_list.split()]:
    if value in winning_set:
      match_count += 1

  return match_count


def addCardMultipliers(count, multiplier, mults_q):
  while len(mults_q) < count:
    mults_q.append(0)

  for i in range(count):
    mults_q[i] += multiplier


def part1(filename):
  total_value = 0
  with open(filename) as inf:
    for line in inf:
      match = line_re.search(line)
      if not match:
        print('Bad line: ' + repr(line))
        continue
      card_no = int(match.group(1))
      match_count = countWins(match.group(2), match.group(3))
      value = 0 if match_count==0 else 2 ** (match_count-1)
      # print(f'card {card_no} {match_count} matches, value {value}')
      total_value += value
  print(f'part1 {total_value}')
      

def part2(filename):
  total_card_count = 0

  mults_q = collections.deque()

  with open(filename) as inf:
    for line in inf:
      # Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53

      match = line_re.search(line)
      if not match:
        print('Bad line: ' + repr(line))
        continue

      if len(mults_q) == 0:
        card_multiplier = 1
      else:
        card_multiplier = mults_q.popleft() + 1
      total_card_count += card_multiplier

      card_no = int(match.group(1))
      match_count = countWins(match.group(2), match.group(3))

      # print(f'Card {card_no}: {card_multiplier} copies, {match_count} wins')

      addCardMultipliers(match_count, card_multiplier, mults_q)
      # print(f'  after card {card_no}: {list(mults_q)}')


  # print(f'total value {total_value}')
  print(f'part2 {total_card_count}')
  

if __name__ == '__main__':
  filename = 'day4.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
