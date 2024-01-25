#!/usr/bin/env python3

"""
Advent of Code 2023, day 21: Step Counter

Flood fill and extrapolation.

I spent __way__ too much time beating my head on the wall with this one.
My solution contains a bunch of constants specific to my input data
(see quickAnswer()) so it won't work with other input data. If I get
bored I'll clean it up and make it more robust.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

"""
grid 131 x 131, start at (65, 65)
goal = 26501365 = 202300 * 131 + 65
'o' even, 'O' odd

type A0: sharp diamond, top point is even, or 'o'
type A1: sharp diamond, top point is odd, or 'O'
type B0: blunt even
type B1: blunt odd
type x0: incomplete type B0 on northeast frontier
type x1: incomplete type B1 on northeast frontier


after D * 131 + 65 steps
  x count = D
    reachable = 3724, whether x-0 or x-1
  A-0 count
    0  1  2  3   4   5
    0, 4, 4, 16, 16, 36
    (( (D+1)//2 )*2) ** 2
    even D: 3642
    odd D: 3776
  A-1 count
    0  1  2  3  4   5
    1, 1, 9, 9, 25, 25
    ((D//2)*2 + 1) ** 2
    even D: 3776
    odd D: 3642
  B-0 count
    0  1  2  3  4  5  6  7  8  9  10
    0  2  4 12 16 30 36 56 64 90 100
    D * (D + (D&1))
    even D: 3724
    odd D: 3729
  B-1 count
    0  1  2  3  4  5  6  7  8  9  10
    0  1  6  9 20 25 42 49 72 81 110
    D * (D + 1 - (D&1))
    even D: 3729
    odd D: 3724


  D == 0: 65 steps, 3776
    A-1: 3776 x1

  D == 1: 196 steps, 33652
    A-1: 3642 x1
    A-0: 3776 x4
    x-1: 3724 x1
    B-0: 3729 x2
    B-1: 3724 x1

      A0
    B0  x1
  A0  A1  A0
    B1  B0
      A0

  D == 2: 327 steps, 93270
    A-1: 3776 x9
    A-0: 3642 x4
    B-1: 3729 x6
    B-0: 3724 x4
    x-0: 3724 x2

         A
       B   b
     A   A   A
   B   B   B   b
 A   A   A   A   A
   B   B   B   B
     A   A   A
       B   B
         A

  Each side has D+1 A diamonds
    outer layer 4 * D, next 4 * (D-1), etc plus center
    total A diamonds = 4 * SUM(1..D) + 1 = 4 * (1/2) D * (D+1)
      = 2 * D * (D+1) + 1
  Each side has D B diamonds, and one side is all short B's or b's
    B * 4 * SUM(1..D) - D
       = 2 * D * (D+1) - D
    b = D

  D == 3:
                  A
                B   B
              A   A   A
            B   B   B   B
          A   A   A   A   A
        B   B   B   B   B   B
      A   A   A  [A]  A   A   A
        B   B   B   B   B   B
          A   A   A   A   A
            B   B   B   B
              A   A   A
                B   B
                  A

  


  D == 4:
  A: 41
  B: 36
  b: 4

                  A
                B   b
              A   A   A
            B   B   B   b
          A   A   A   A   A
        B   B   B   B   B   b
      A   A   A   A   A   A   A
    B   B   B   B   B   B   B   b
  A   A   A   A  [A]  A   A   A   A
    B   B   B   B   B   B   B   B
      A   A   A   A   A   A   A
        B   B   B   B   B   B
          A   A   A   A   A
            B   B   B   B
              A   A   A
                B   B
                  A

D = 202300
A = 81850984601
B = 81850782300
b = 202300

A(0, 0): Counter({'O': 3776, 'o': 3642, '#': 1158, '.': 5})
A(-131, 0): Counter({'o': 3776, 'O': 3642, '#': 1158, '.': 5})
A(131, 0): Counter({'o': 3776, 'O': 3642, '#': 1158, '.': 5})
A(0, -131): Counter({'o': 3776, 'O': 3642, '#': 1158, '.': 5})
A(0, 131): Counter({'o': 3776, 'O': 3642, '#': 1158, '.': 5})
B(0, 0): Counter({'O': 3727, 'o': 3724, '#': 1124, '.': 5})
B(131, 0): Counter({'o': 3729, 'O': 3724, '#': 1124, '.': 3})
B(131, -131): Counter({'O': 3729, 'o': 3724, '#': 1124, '.': 3})
B(0, -131): Counter({'o': 3729, 'O': 3724, '#': 1124, '.': 3})
Total reachable after 196 steps: 33652

aha, there are 4 type B's: (is on NE wall) * (is top row Oo or oO)
  NE of center, top row is Oo
  B Oo is 3729
  B oO is 3724
  b Oo is 3727 (-2)
  b oO is unchanged

A * 3776 + B * 3724 + b * 3727 = 613882385110676
  wrong, too high
  how about if b['O'] = 3722
A * 3776 + B * 3724 + b * 3722 = 613882384099176
  still too high

quickAnswer(26501365) = 608603023105276
  YES!!!!!!!!

after 65 steps, can reach 3776 plots (3642 even, 3776 odd)
  1 diamond A
after 196 steps, can reach 33652 plots (33652 even, 33248 odd)
  5A 4B
  2 not yet filled odd blocks on northeast face
after 327 steps, can reach 93270 plots (92596 even, 93270 odd)
  13A 12B


with no obstuctions:


    x  0: 1

    x
   x x  1: 4
    x


    x
   x x
  x x x  2: 9
   x x
    x

     x
    x x
   x x x
  x x x x  3: 16
   x x x
    x x
     x

f(x) = (n+1)^2


    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A
    B   B   B   B   B   B   B   B   B   B   B   B   B   B   B   B
  A   A   A   A   A   A   A   A   A   A   A   A   A   A   A   A


after 63 steps, can reach 3512 plots
  grow by 136 vs 127, diff = -9
after 64 steps, can reach 3642 plots
  grow by 130 vs 129, diff = -1
after 65 steps, can reach 3776 plots
  grow by 134 vs 131, diff = -3
after 66 steps, can reach 3906 plots
  grow by 130 vs 133, diff = 3


after 195 steps, can reach 33248 plots
  grow by 396 vs 391, diff = -5
after 196 steps, can reach 33652 plots
  grow by 404 vs 393, diff = -11
after 197 steps, can reach 34038 plots
  grow by 386 vs 395, diff = 9
after 198 steps, can reach 34444 plots
  grow by 406 vs 397, diff = -9
after 199 steps, can reach 34834 plots
  grow by 390 vs 399, diff = 9




A=1
f(64) = 3642
f(65) = 3642

                  A


5A+4B (or prev + 4(A+B))
  A+=4  B+=4
  A = 1+4
  B = 2*1*2
f(64+131=195) = 33248
                  A
                B   B
              A   A   A
                B   B
                  A


(9+4+1=14)A + (2+3+2+3+2 = 12)B
  A+=9  B+=8 (4*2)
  A = 1+4+9
  B = 2*2*3
f(64+2*131=326) = 92596
                  A
                B   B
              A   A   A
            B   B   B   B
          A   A   A   A   A
            B   B   B   B
              A   A   A
                B   B
                  A

30A + 24B  (B is 3*4 + 3*4 or 2*3*4 or 2(n)(n+1))
  A+=16 B+=12
  A = 1+4+9+16
  B = 2*3*4

                  A
                B   B
              A   A   A
            B   B   B   B
          A   A   A   A   A
        B   B   B   B   B   B
      A   A   A   A   A   A   A
        B   B   B   B   B   B
          A   A   A   A   A
            B   B   B   B
              A   A   A
                B   B
                  A



A has 5 unreachable cells and a few edges that don't fill until
move 65 (mod 131)

B fills at (67 mod 131) with 3 unreachable


goal = 26501365 = 202300 * 131 + 65

--another method--
Compute the amount of coverage at each step of filling the initial grid
from the starting point, each corner, and the center of each edge.

center: fillng from steps 1-131
left, right, up down: enter on step 67
up-left, up-right, down-left, down-right: step 133


9 10 11 12 13
   1  2  3
   4  0  5
   6  7  8

f, 139: expect to start at 133+262 = 395
  actual 395
10: expect at 67 + 65 + 131 = 263
  actual 264

"""

import sys, re, collections
from common import *
from draw_grid import drawGrid

def tryCell(grid, q, r, c):
  # enqueue this point if it is not a #
  if (r < 0 or r >= len(grid)
      or c < 0 or c >= len(grid[0])
      or grid[r][c] == '#'):
    return

  # if (r,c) not in q: print(f'  q {r}, {c}')
  q.add((r,c))


def bfsCount(grid, r, c, max_steps, q):
  for step_no in range(1, max_steps+1):
    qlen = len(q)
    q2 = set()

    # for i in range(qlen):
    #   r,c = q.popleft()
    for r,c in q:
      tryCell(grid, q2, r-1, c)
      tryCell(grid, q2, r+1, c)
      tryCell(grid, q2, r, c-1)
      tryCell(grid, q2, r, c+1)

    qlen = len(q2)
    # print(f'after {step_no} steps, can reach {qlen} plots')
    q = q2
    
  return len(q2)


def part1(filename):
  with open(filename) as inf:
    grid = readGrid(inf, True)
  start = gridSearch(grid, 'S')
  # print(f'grid {len(grid)} x {len(grid[0])}, start at {start!r}')
  # print(f'start at {start!r}')
  fill_grid = deepCopyGrid(grid)
  # printGrid(grid)
  # printGrid(fill_grid)

  # q = collections.deque()
  q = set()
  q.add(start)
  r,c = start
  fill_grid[r][c] = '.'
  count = bfsCount(fill_grid, r, c, 64, q)
  print(f'part1 {count}')



class Quadrant:
  def __init__(self, row0, col0, height, width):
    """
    """
    self.row0 = row0
    self.col0 = col0

    # size of each quadrant
    self.height = height
    self.width = width

    # counters[0] is the total number of reachable cells on even steps
    # counters[0] is for odd steps
    self.counters = [0, 0]

    # index of the first step in which cells in this quadrant are reachable
    self.first_step = None

    # list of cells that were reached in step 'first_step'
    self.first_step_cell_list = []

    # step_counters[step_no - first_step] = [# of new cells reached this step]
    self.step_counters = []

    # index of the step when every reachable cell in this quadrant has
    # been reached
    self.last_step = None

  def name(self):
    qr = self.row0 / self.height
    qc = self.col0 / self.width
    return f'q({qr},{qc})'


class BFSState:
  def __init__(self, grid, quadrant_height, quadrant_width):
    self.grid = grid
    self.q = collections.deque()
    self.quadrant_height = quadrant_height
    self.quadrant_width = quadrant_width
    self.step_idx = 0
    self.fill_char = '.'


def tryCell2(bfs, r, c):
  # fill and enqueue this point if it is empty
  if (r < 0 or r >= len(bfs.grid)
      or c < 0 or c >= len(bfs.grid[0])
      or bfs.grid[r][c] != '.'):
    return

  bfs.grid[r][c] = bfs.fill_char
  # if (r,c) in q: print(f'  dup {r}, {c}')
  # q.add((r,c))
  bfs.q.append((r,c))


def bfsFill(grid, r, c, max_steps, start,
            image_file_name_pattern = None,
            do_write_image_this_step_fn = lambda x: True):

  bfs = BFSState(grid, 131, 131)
  bfs.q.append(start)

  # [sum_even_steps, sum_odd_steps]
  cumulative = [0, 0]
  is_odd = 0
  prev_qlen = 1
  fill_chars = ['o', 'O']
  for step_no in range(1, max_steps+1):
    is_odd = 1 - is_odd
    qlen = len(bfs.q)
    bfs.fill_char = fill_chars[is_odd]

    for i in range(qlen):
      r,c = bfs.q.popleft()
      tryCell2(bfs, r-1, c)
      tryCell2(bfs, r+1, c)
      tryCell2(bfs, r, c-1)
      tryCell2(bfs, r, c+1)

    cumulative[is_odd] += len(bfs.q)
    # print(f'after {step_no} steps, can reach {cumulative[is_odd]} plots ({cumulative[0]} even, {cumulative[1]} odd)')

    if image_file_name_pattern and do_write_image_this_step_fn(step_no):
      drawGrid(grid, image_file_name_pattern % step_no)

  print(f'after {step_no} steps, can reach {cumulative[is_odd]} plots ({cumulative[0]} even, {cumulative[1]} odd)')


def makeOddDuplicate(src, count):
  assert (count % 2) == 1
  w = len(src[0])
  h = len(src)
  start = gridSearch(src, 'S')
  src[start[0]][start[1]] = '.'

  grid = createGrid(h*count, w*count, True)

  for i in range(count):
    for j in range(count):
      pasteGrid(grid, i*h, j*w, src)
  grid[h*(count//2)+start[0]][w*(count//2)+start[1]] = 'S'

  return grid


def drawPartial(in_filename, dup_factor, iter_count, out_filename):
  # with open(in_filename) as inf:
  #   grid = readGrid(inf, True)

  # grid = make3x3(in_filename)
  grid = makeOddDuplicate(in_filename, dup_factor)

  start = gridSearch(grid, 'S')
  # fill_grid = deepCopyGrid(grid)

  r,c = start
  grid[r][c] = '.'
  bfsFill(grid, r, c, iter_count, start)
  # printGrid(grid)
  grid[r][c] = 'S'
  drawGrid(grid, out_filename,
           cell_color_map={'O': (0,0,255), 'o': (150,150,255)})




def drawBorders(in_filename, out_filename):
  """
  In the center diamond, there are 1158 '#' cells, 7162 '.', 1 'S'
  In the other diamod, there are 1124 '#' cells, 7197 '.'
  """
  grid = makeOddDuplicate(in_filename, 3)

  start = gridSearch(grid, 'S')
  fill_grid = deepCopyGrid(grid)

  counter = collections.Counter()
  r,c = start
  for i in range(66):
    """
    grid[r-i][c-65+i] = 'O'
    grid[r-i][c+65-i] = 'O'
    grid[r+i][c-65+i] = 'O'
    grid[r+i][c+65-i] = 'O'
    counter.update(grid[r-i][c-64+i : c+65-i])
    if i > 0:
      counter.update(grid[r+i][c-64+i : c+65-i])
    """
    grid[r+65-i][c+i] = 'O'
    grid[r+65-i][c+130-i] = 'O'
    grid[r+65+i][c+i] = 'O'
    grid[r+65+i][c+130-i] = 'O'
    counter.update(grid[r+65-i][c+i+1 : c+130-i])
    if i > 0:
      counter.update(grid[r+65+i][c+i+1 : c+130-i])


  print(repr(counter))
  drawGrid(grid, out_filename,
           cell_color_map={'O': (0,0,255), 'o': (150,150,255)})


def bfsFillAndSave(grid, r, c, max_steps, q, outf_pattern):

  is_even = 0
  prev_qlen = 1
  fill_chars = ['O', 'o']
  for step_no in range(1, max_steps+1):
    is_even = 1 - is_even
    qlen = len(q)
    q2 = set()
    fill = fill_chars[is_even]

    # for i in range(qlen):
    #   r,c = q.popleft()
    for r,c in q:
      grid[r][c] = fill
      tryCell(grid, q2, r-1, c)
      tryCell(grid, q2, r+1, c)
      tryCell(grid, q2, r, c-1)
      tryCell(grid, q2, r, c+1)

    qlen = len(q2)
    q = q2

    # how much would we grow if there were no obstructions?
    # full_growth = (step_no+1)**2 - step_no**2

    print(f'after {step_no} steps, can reach {qlen} plots')
    drawGrid(grid, outf_pattern % step_no,
             cell_color_map={'O': (0,0,255), 'o': (150,150,255)})

    # print(f'  grow by {qlen - prev_qlen} vs {full_growth}, diff = {full_growth - (qlen - prev_qlen)}')
    # prev_qlen = qlen

  # for r,c in q:
  #   grid[r][c] = 'O'


def drawFrames(infile, dup_count, outf_name_pattern):
  with open(infile) as inf:
    grid = readGrid(grid, True)
  grid = makeOddDuplicate(grid, dup_count)
  start = gridSearch(grid, 'S')

  q = set()
  q.add(start)
  r,c = start
  grid[r][c] = '.'
  # bfsFillAndSave(grid, r, c, max_iters, q, 'day21.small.%03d.png')
  bfsFill(grid, r, c, max_iters, q)


def censusQuadrants(inf_name, dup_count):
  grid = makeOddDuplicate(inf_name, dup_count)
  start = gridSearch(grid, 'S')
  quadrant_width = len(grid[0]) // dup_count
  quadrant_height = len(grid) // dup_count
  print(f'{quadrant_height}, {quadrant_width}')
  q = set()
  q.add(start)
  grid[start[0]][start[1]] = '.'

  step_counters = []

  quadrant_counters = [collections.Counter() for _ in range(dup_count * dup_count)]
  for qr in range(dup_count):
    for qc in range(dup_count):
      qi = qr * dup_count + qc
      counter = quadrant_counters[qi]
      origin_r = quadrant_height * qr
      origin_c = quadrant_width * qc
      for r in range(origin_r, origin_r + quadrant_height):
        for c in range(origin_c, origin_c + quadrant_width):
          counter.update(grid[r][c])

  step_counters.append([dict(qc) for qc in quadrant_counters])
  print(f'step_counters[0] = {step_counters[0]!r}')

  is_even = 0
  prev_qlen = 1
  fill_chars = ['O', 'o']
  r,c = start
  step_no = 0

  while len(q) != 0:

    step_no += 1

    # if step_no == 6:
    #   drawGrid(grid, 'day21.png',
    #            cell_color_map={'O': (0,0,255), 'o': (150,150,255)})
    #   break

    is_even = 1 - is_even
    qlen = len(q)
    q2 = set()
    fill = fill_chars[is_even]

    # for i in range(qlen):
    #   r,c = q.popleft()
    for r,c in q:
      quadrant = (r//quadrant_height) * dup_count + (c//quadrant_width)
      counter = quadrant_counters[quadrant]
      counter.subtract(grid[r][c])
      grid[r][c] = fill
      counter.update(fill)
      tryCell2(grid, q2, r-1, c)
      tryCell2(grid, q2, r+1, c)
      tryCell2(grid, q2, r, c-1)
      tryCell2(grid, q2, r, c+1)

    qlen = len(q2)
    q = q2

    step_counters.append([dict(qc) for qc in quadrant_counters])
    for i, qc in enumerate(quadrant_counters):
      print(f'step_counters[{step_no}][{i}] = {qc!r}')
    print()

  drawGrid(grid, 'day21.png',
           cell_color_map={'O': (0,0,255), 'o': (150,150,255)})
  print('wrote day21.png')


class Diamond:
  def __init__(self, is_sharp, top_row, top_left_col, is_incomplete_northeast = False):
    self.is_sharp = is_sharp  # True: type A, False: type B
    self.top_row = top_row
    self.top_left_col = top_left_col
    self.is_incomplete_northeast = is_incomplete_northeast

  def __str__(self):
    return f'{self.label()} at ({self.top_row},{self.top_left_col})'

  def dtype(self):
    if self.is_sharp:
      return 'A'
    else:
      if self.is_incomplete_northeast:
        return 'x'
      else:
        return 'B'

  def parity(self):
    return ['0', '1'][(self.top_row + self.top_left_col) & 1]

  def label(self):
    return self.dtype()+'-'+self.parity()

  def color(self):
    return {'A': 'r', 'B': 'g', 'x': 'y'}[self.dtype()]
    
  def rows(self):
    """
    Produces an iterable of (row, left, right)
    """
    if self.is_sharp:
      for i in range(66):
        left = self.top_left_col - i
        right = self.top_left_col + i
        yield (self.top_row + i, left, right)
        if i != 130-i:
          yield (self.top_row + 130 - i, left, right)
    else:
      for i in range(65):
        left = self.top_left_col - i
        right = self.top_left_col + 1 + i
        yield (self.top_row + i, left, right)
        yield (self.top_row + 129 - i, left, right)


def listDiamonds(grid, step_count):
  """
  Generate definitions for all diamonds filled at this step count.
  """

  n_layers = (step_count + 66) // 131
  # print(f'diamonds for {n_layers} layers')

  start = gridSearch(grid, 'S')

  diamond_list = []

  # A-type diamonds
  # origin of each is northern point, so first one is start_x, start_y-65
  # offsets_a = [ (0,0), (-131,0), (131,0), (0,-131), (0,131), ]
  diamond_list.append(Diamond(True, start[0]-65, start[1]))
  for layer_no in range(1, n_layers):
    r = -(layer_no * 131)
    c = 0
    for i in range(layer_no):
      diamond_list.append(Diamond(True, start[0] + r - 65, start[1] + c))
      diamond_list.append(Diamond(True, start[0] + c - 65, start[1] - r))
      diamond_list.append(Diamond(True, start[0] - r - 65, start[1] - c))
      diamond_list.append(Diamond(True, start[0] - c - 65, start[1] + r))
      c += 131
      r += 131

  # B-type diamonds, with blunt (2-wide) ends
  """
        o O
      o O o O
    o O o O o O
    O o O o O o
      O o O o
        O o
  """
  for layer_no in range(1, n_layers):
    r = 1 - 131 * layer_no
    c = 65
    for i in range(layer_no):
      if layer_no == n_layers-1:
        diamond_list.append(Diamond(False, start[0] + r, start[1] + c, True))
      else:
        diamond_list.append(Diamond(False, start[0] + r, start[1] + c))
      diamond_list.append(Diamond(False, start[0] - r - 129, start[1] + c))
      diamond_list.append(Diamond(False, start[0] + r, start[1] - c - 1))
      diamond_list.append(Diamond(False, start[0] - r - 129, start[1] - c - 1))
      c += 131
      r += 131

  return diamond_list


def outlineDiamonds(grid, step_count, draw_a = True, draw_b = True):
  """
  Draw the outlines of sector diamonds, to test the boundary logic before
  using it to do surveys.
  """

  diamond_list = listDiamonds(grid, step_count)
    
  for d in diamond_list:
    f = d.color()
    # print(d)
    # print('  ' + d.label())
    color = grid[d.top_row][d.top_left_col]
    for (row,left,right) in d.rows():
      grid[row][left] = f
      grid[row][right] = f
    


def surveyDiamonds(grid, step_count):
  """
  Count the cells in each color, split by diamond.
  Center diamonds with sharp corners are type A.
  Other diamonds with blunt corners are type B.

  type A total=8581  'O': 3776, 'o': 3642, '#': 1158, '.': 5
  type B total=8580
    most {'o': 3729, 'O': 3724, '#': 1124, '.': 3}
    northeast {'O': 3727, 'o': 3724, '#': 1124, '.': 5}
  """

  diamond_list = listDiamonds(grid, step_count)

  r,c = start
  grid[r][c] = 'o'

  if (step_count & 1) == 0:
    # even
    reachable = 'o'
    non_reachable = 'O'
  else:
    reachable = 'O'
    non_reachable = 'o'


  # diamond label + n_reachable -> count
  label_and_reachable = collections.Counter()

  total_reachable = 0
  for d in diamond_list:
    counter = collections.Counter()
    for (row,left,right) in d.rows():
      counter.update(grid[row][left:right+1])
    # print(f'{d} {counter[reachable]} / {counter[non_reachable]} / {counter["#"]}')
    label_and_reachable.update([(d.label(), counter[reachable])])
    # print(counter)
    total_reachable += counter[reachable]

  print(f'Total reachable after {step_count} steps: {total_reachable}')
  print('types and reachables')
  for key, copies in label_and_reachable.items():
    label, reachable = key
    print(f'{label}: {reachable} x{copies}')




def quickAnswer(iter_count):
  """
  quickAnswer(26501365) = 608603023105276
  YES!!!!!!!!
  """
  # print(f'{iter_count} iters')
  D = (iter_count - 65) // 131
  # print(f'D = {D}')

  even = (D & 1) == 0
  
  x = D
  xc = x * 3724
  # print(f'x: {x} * 3724 = {xc}')

  a0 = (( (D+1)//2 )*2) ** 2
  a0f = 3642 if even else 3776
  a0c = a0 * a0f

  a1 = ((D//2)*2 + 1) ** 2
  a1f = 3776 if even else 3642
  a1c = a1 * a1f

  b0 = D * (D + (D&1))
  b0f = 3724 if even else 3729
  b0c = b0 * b0f

  b1 = D * (D + 1 - (D&1))
  b1f = 3729 if even else 3724
  b1c = b1 * b1f

  total = xc + a0c + a1c + b0c + b1c
  # print(f'{total} = x ({xc}*3724) + a0 ({a0}*{a0f}) + a1 ({a1}*{a1f}) + b0 ({b0}*{b0f}) + b1 ({b1}*{b1f})')
  return total
        


def part2(filename):

  # drawBorders('day21.in.txt', 'day21.png')

  # args = sys.argv[1:]
  # if len(args) != 4:
  #   print('day21.py infile board-X iters outfile')
  #   sys.exit(1)
  # drawPartial(args[0], int(args[1]), int(args[2]), args[3])

  # drawAllFrames('day21.in.txt', 131+65)
  # drawAllFrames('day21.small', 500, 91, 'day21/small_%03d.png')

  # track the number of cells in each color in each copy of the board
  # censusQuadrants('day21.in.txt', 5)

  # with open('day21.in.txt') as inf:
  #   grid = readGrid(inf, True)
  # drawGrid(grid, 'day21.000.png')


  n_layers = int(sys.argv[1]) + 1
  iter_count = 65 + 131 * (n_layers-1)

  quickAnswer(iter_count)
  exit(0)

  with open(filename) as inf:
    grid = readGrid(filename, True)
  grid = makeOddDuplicate(grid, (n_layers-1) * 2 + 1)

  start = gridSearch(grid, 'S')

  r,c = start
  grid[r][c] = '.'
  bfsFill(grid, r, c, iter_count, start)

  # 'day21/step%04d.png',
  # lambda x: (x % 131) == 65)
  grid[r][c] = 'S'


  # outlineDiamonds(grid, iter_count, True, True)
  surveyDiamonds(grid, iter_count)
  """
  counter = collections.Counter()
  for row in grid:
    counter.update(row)
  print(counter)
  """
  # drawGrid(grid, 'day21.png')
  # drawGrid(grid, 'day21.png', {'y', (255,255,0)})

  
if __name__ == '__main__':
  filename = 'day21.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]

  part1(filename)
  print(f'part2 {quickAnswer(26501365)}')
  
