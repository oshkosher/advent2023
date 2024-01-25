#!/usr/bin/env python3

"""
Advent of Code 2023, day 7: Camel Cards

Simplified poker hands, with jokers.

Ed Karrels, ed.karrels@gmail.com, December 2023
"""

import sys

HAND_HIGH_CARD = 0
HAND_ONE_PAIR = 1
HAND_TWO_PAIR = 2
HAND_THREE = 3
HAND_FULL_HOUSE = 4
HAND_FOUR = 5
HAND_FIVE = 6


card_value = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
              'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

card_value2 = {'J': 1,
              '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
              'T': 10, 'Q': 12, 'K': 13, 'A': 14}


def handType(hand):
  assert len(hand) == 5
  counters = {}
  for card in hand:
    if card in counters:
      counters[card] += 1
    else:
      counters[card] = 1
  # counts = [(x[1], x[0]) for x in counters.items()]
  counts = list(counters.values())
  counts.sort()
  counts.reverse()

  # print(f'{hand}: {counts}')

  if counts[0] == 5:
    return HAND_FIVE
  elif counts[0] == 4:
    return HAND_FOUR
  elif counts[0] == 3:
    if counts[1] == 2:
      return HAND_FULL_HOUSE
    else:
      return HAND_THREE
  elif counts[0] == 2:
    if counts[1] == 2:
      return HAND_TWO_PAIR
    else:
      return HAND_ONE_PAIR
  else:
    return HAND_HIGH_CARD


def handType2(hand):
  assert len(hand) == 5
  joker_count = 0
  counters = {}
  for card in hand:
    if card == 'J':
      joker_count += 1
    else:
      if card in counters:
        counters[card] += 1
      else:
        counters[card] = 1

  if joker_count == 5:
    return HAND_FIVE

  # counts = [(x[1], x[0]) for x in counters.items()]
  counts = list(counters.values())
  counts.sort()
  counts.reverse()

  # print(f'{hand}: {counts}')
  
  counts[0] += joker_count

  if counts[0] == 5:
    return HAND_FIVE
  elif counts[0] == 4:
    return HAND_FOUR
  elif counts[0] == 3:
    if counts[1] == 2:
      return HAND_FULL_HOUSE
    else:
      return HAND_THREE
  elif counts[0] == 2:
    if counts[1] == 2:
      return HAND_TWO_PAIR
    else:
      return HAND_ONE_PAIR
  else:
    return HAND_HIGH_CARD


def lessThan(hand1, hand2):
  # returns true if hand2 beats hand1
  t1 = handType(hand1)
  t2 = handType(hand2)
  if t1 != t2:
    return t1 < t2

  for i in range(5):
    c1 = card_value[hand1[i]]
    c2 = card_value[hand2[i]]
    if c1 != c2:
      return c1 < c2

  return False


def lessThan2(hand1, hand2):
  # returns true if hand2 beats hand1
  t1 = handType2(hand1)
  t2 = handType2(hand2)
  if t1 != t2:
    return t1 < t2

  for i in range(5):
    c1 = card_value2[hand1[i]]
    c2 = card_value2[hand2[i]]
    if c1 != c2:
      return c1 < c2

  return False


class Hand:
  def __init__(self, hand, bid):
    self.hand = hand
    self.bid = bid

  def __lt__(self, that):
    return lessThan(self.hand, that.hand)


class Hand2:
  def __init__(self, hand, bid):
    self.hand = hand
    self.bid = bid

  def __lt__(self, that):
    return lessThan2(self.hand, that.hand)

  

def part1(filename):
  winnings = 0
  with open(filename) as inf:
    hands = []
    for line in inf:
      hand, bid = line.split()
      h = Hand(hand, int(bid))
      hands.append(h)
      # t = handType(hand)
      # print(f'{hand}: {t}')

    hands.sort()
    for i, hand in enumerate(hands):
      w = hand.bid * (i+1)
      # print(f'{i} {hand.hand} {hand.bid}*{i+1} = {w}')
      winnings += w
  print(f'part1 {winnings}')
  

def part2(filename):
  winnings = 0
  with open(filename) as inf:
    hands = []
    for line in inf:
      hand, bid = line.split()
      # print(f'hand {hand} type {handType2(hand)}')
      h = Hand2(hand, int(bid))
      hands.append(h)
      # t = handType(hand)
      # print(f'{hand}: {t}')

    hands.sort()
    for i, hand in enumerate(hands):
      w = hand.bid * (i+1)
      # print(f'{i} {hand.hand} {hand.bid}*{i+1} = {w}')
      winnings += w
      
  print(f'part2 {winnings}')
  

if __name__ == '__main__':
  filename = 'day7.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  part1(filename)
  part2(filename)
