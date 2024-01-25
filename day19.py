#!/usr/bin/env python3

"""
Advent of Code 2023, day 19: Aplenty

Simplify a lists of rules into a tree.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, re, collections, time

workflow_re = re.compile(r'([a-z]+){(.*)}')
rule_re = re.compile(r'([xmas])([<>])(\d+):(A|R|[a-z]+)')
ratings_re = re.compile(r'{x=(\d+),m=(\d+),a=(\d+),s=(\d+)}')

rating_idx = {'x': 0, 'm': 1, 'a': 2, 's': 3}
rating_name = 'xmas'

Rule = collections.namedtuple \
  ('Rule', ['rating_idx', 'compare_fn', 'value', 'dest', 'compare_symbol'])

def isLessThan(a, b):
  return a < b

def isGreaterThan(a, b):
  return a > b

def parseRule(s):
  # returns Rule object
  m = rule_re.match(s)
  assert m, s
  compareFn = isLessThan if m.group(2)=='<' else isGreaterThan
  # return (rating_idx[m.group(1)], compareFn, int(m.group(3)), m.group(4))
  return Rule(rating_idx[m.group(1)], compareFn, int(m.group(3)), m.group(4),
              m.group(2))

def readInput(inf):
  # name: ([rules], default)
  # each rule is ([xmas], compareFn, value, dest)
  workflows = {}
  while True:
    line = inf.readline().strip()
    if not line: break

    wm = workflow_re.match(line)
    if not wm:
      print('Bad workflow: ' + repr(line))
      continue
    name = wm.group(1)
    rule_strs = wm.group(2).split(',')
    rules = [parseRule(s) for s in rule_strs[:-1]]
    default = rule_strs[-1]
    workflows[name] = (rules, default)

  parts = []
  while True:
    line = inf.readline()
    if not line: break
    rm = ratings_re.match(line)
    assert rm
    ratings = tuple(int(x) for x in rm.group(1,2,3,4))
    parts.append(ratings)

  return workflows, parts


def isPartAccepted(part, workflows):
  wf_name = 'in'

  while wf_name not in {'A', 'R'}:
    wf = workflows[wf_name]
    rules = wf[0]
    wf_name = wf[1]
    # for (rating, compareFn, value, dest) in rules:
    for rule in rules:
      if rule.compare_fn(part[rule.rating_idx], rule.value):
        wf_name = rule.dest
        break
    # print('  ' + wf_name)

  return wf_name == 'A'


def part1(workflows, parts):

  # print(repr(workflows))
  # for x in workflows.items():
  #   print(repr(x))
  # print()
  # for x in parts:
  #   print(repr(x))

  s = 0
  for part in parts:
    if isPartAccepted(part, workflows):
      # print(f'accepted {part!r}')
      s += sum(part)
    else:
      # print(f'rejected {part!r}')
      pass
    
  print(f'part1 {s}')


def listToRanges(lst):
  lo = 1
  for v in lst:
    yield (lo, v)
    lo = v
  yield (lo, 4001)


def secondsToHMS(s):
  h = int(s / 3600)
  s -= h * 3600
  m = int(s/60)
  s -= m * 60
  return f'{h:02}h{m:02}m{s:05.2f}s'

def isWorkflowATree(workflows):
  visits = {}
  order = []
  traverseWorkflows(workflows, visits, order, 'in')
  print(f'{len(visits)} nodes visited out of {len(workflows)}')
  for v in visits.values():
    if v > 1: return False
  return True

def traverseWorkflows(workflows, visits, order, name):
  if name in {'A', 'R'}:
    return
  
  node = workflows[name]
  order.append(name)
  if name in visits:
    visits[name] += 1
    if visits[name] < 2:
      print(f'cycle at {order!r}')
  else:
    visits[name] = 1

    for rule in node[0]:
      traverseWorkflows(workflows, visits, order, rule.dest)
    traverseWorkflows(workflows, visits, order, node[1])

  del(order[-1])

def partRangeSize(p):
  prod = 1
  for r in p:
    prod *= (r[1] - r[0])
  return prod

def traverseAcceptTree(workflows, name, part_ranges, stack, accept):
  if name == 'R':
    return
  
  if name == 'A':
    n = partRangeSize(part_ranges)
    stack_str = '[' + ' '.join(stack) + ']'
    # print(f'accept {n}=[{part_ranges[0][0]}-{part_ranges[0][1]},{part_ranges[1][0]}-{part_ranges[1][1]},{part_ranges[2][0]}-{part_ranges[2][1]},{part_ranges[3][0]}-{part_ranges[3][1]}] via {stack_str}')
    accept[0] += n
    return

  # print(f'traverse {name}')
  stack.append(name)
  part_ranges = part_ranges.copy()
  node = workflows[name]
  for rule in node[0]:
    r = part_ranges[rule.rating_idx]
    if rule.compare_symbol == '<':
      # if all remaining values are already out of range, skip this
      if rule.value <= r[0]:
        continue
      part_ranges[rule.rating_idx] = (r[0], rule.value)
      traverseAcceptTree(workflows, rule.dest, part_ranges, stack, accept)
      part_ranges[rule.rating_idx] = (rule.value, r[1])
    else:
      if rule.value+1 >= r[1]:
        continue
      part_ranges[rule.rating_idx] = (rule.value+1, r[1])
      traverseAcceptTree(workflows, rule.dest, part_ranges, stack, accept)
      part_ranges[rule.rating_idx] = (r[0], rule.value+1)

  traverseAcceptTree(workflows, node[1], part_ranges, stack, accept)
  del(stack[-1])
  

def part2_brute(workflows, parts):

  # Scan all the rules for decision points for each rating
  # Make a sorted list of decision points for each rating.
  # The decision point is always the value when there is a difference
  # between how (value-1) and (value) are handled.

  rating_dps = [set() for _ in range(4)]
  for workflow in workflows.values():
    rules = workflow[0]
    for rule in rules:
      offset = 0 if rule.compare_symbol=='<' else 1
      rating_dps[rule.rating_idx].add(rule.value + offset)

  rating_range_product = 1
  for i in range(4):
    l = list(rating_dps[i])
    l.sort()
    rating_dps[i] = l
    print(f'{rating_name[i]}: {" ".join([str(x) for x in l])}')
    rating_range_product *= len(rating_dps[i]) + 1

  print(f'{rating_range_product} combos to test')


  check_count = 0
  report_interval = 1000000
  report_countdown = report_interval

  ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
  print(f'Start at {ts}')
  start_time = time.time()
  
  accepted_count = 0
  for rx in listToRanges(rating_dps[0]):
    for rm in listToRanges(rating_dps[1]):
      for ra in listToRanges(rating_dps[2]):
        for rs in listToRanges(rating_dps[3]):
          if isPartAccepted((rx[0], rm[0], ra[0], rs[0]), workflows):
            accepted_count += ((rx[1] - rx[0])
                               * (rm[1] - rm[0])
                               * (ra[1] - ra[0])
                               * (rs[1] - rs[0]))
          check_count += 1
          report_countdown -= 1
          if report_countdown == 0:
            elapsed = time.time() - start_time
            hms = secondsToHMS(elapsed)
            report_countdown = report_interval
            rate = check_count / elapsed
            eta = (rating_range_product - check_count) / rate
            done_hms = secondsToHMS(eta)
            sys.stdout.write(f'\r{hms} {check_count}/{rating_range_product}, {100. * check_count / rating_range_product:.3f}% done, eta {done_hms}')

            
  sys.stdout.write(f'\r{secondsToHMS(time.time() - start_time)} {check_count}/{rating_range_product}, {100. * check_count / rating_range_product:.3f}% done\n')
            

  ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
  print(f'done at {ts}')
  print(f'{accepted_count} accepted')

  """
  Start at 2024-01-01 08:40:41
  3h15m33.26s 5066000000/4990510008, 101.513% done, eta 0h-2m-54.84s
  done at 2024-01-01 11:56:15
  121158073425385 accepted
  """
  

def part2(workflows, parts):
  # check if the rules form a tree
  # print('is tree: ' + str(isWorkflowATree(workflows)))
  # Great! This means we can use a much simpler approach.

  accept = [0]
  part_ranges = [(1, 4001), (1, 4001), (1, 4001), (1, 4001)]
  stack = []
  traverseAcceptTree(workflows, 'in', part_ranges, stack, accept)
  print(f'part2 {accept[0]}')

  # 121158073425385


if __name__ == '__main__':
  filename = 'day19.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  with open(filename) as inf:
    workflows, parts = readInput(inf)
  part1(workflows, parts)
  part2(workflows, parts)
