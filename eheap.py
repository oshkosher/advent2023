#!/usr/bin/env python3

"""
I made my own heap class so I could include a decreaseKey() method,
which make Dijkstra's algorithm more efficent than remove+add.
"""

class Heap:
  """
  Heap for objects with __lt__ overridden.
  An attribute _eheap_index_ will be added to each object.
  An AttributeError will be thrown if an element isn't an object with
  settable attributes.
  """
  def __init__(self, input_array = None):
    self.array = []
    if input_array:
      self.array.extend(input_array)
      self.heapify()
    # self.isValid()

  def add(self, e):
    i = len(self.array)
    self.array.append(e)
    # e._eheap_index_ = i
    self.siftUp(i)

  def get(self, i):
    return self.array[i]

  def __len__(self):
    return len(self.array)

  def pop(self):
    """
    Remove and return smallest element, or None if empty.
    """
    if not self.array: return None

    size = len(self.array)
    result = self.array[0]
    self.array[0] = self.array[size-1]
    self.entryMoved(0)
    del(self.array[size-1])
    self.siftDown(0)
    return result

  def heapify(self):
    start = (len(self.array) - 1) // 2
    for i in range(start, -1, -1):
      self.siftDown(i)
    for i in range(len(self.array)):
      self.entryMoved(i)

  def siftDown(self, i):
    """
    self.array[i] might be too big. Swap it with the lesser of its
    children until it's in the right place.
    """
    size = len(self.array)
    while True:
      ci = self.indexLeftChild(i)
      if ci >= size:
        break
      min_child_i = ci
      if ci + 1 < size and self.array[ci+1] < self.array[ci]:
        min_child_i = ci + 1
      # don't swap if parent is equal, and only use the less-than operator.
      if not (self.array[min_child_i] < self.array[i]):
        break
      self.swap(i, min_child_i)
      i = min_child_i

  def siftUp(self, i):
    """
    self.array[i] might be too small. Swap it with its parent until
    it's in the right place.
    """
    while i > 0:
      pi = self.indexParent(i)
      # don't swap if parent is equal, and only use the less-than operator.
      if not (self.array[i] < self.array[pi]):
        break
      self.swap(pi, i)
      i = pi

  def decreaseKey(self, node):
    """
    The key for array[i] has decreased, so it may need to sift up.
    """
    # check that its _eheap_index_ has been kept up-to-date
    i = node._eheap_index_
    assert node == self.array[i]
    self.siftUp(i)
    # self.isValid()

  def indexParent(self, i):
    return (i - 1) >> 1

  def indexLeftChild(self, i):
    return (i * 2) + 1

  def indexrightChild(self, i):
    return (i * 2) + 2

  def swap(self, i, j):
    tmp = self.array[i]
    self.array[i] = self.array[j]
    self.array[j] = tmp
    self.entryMoved(i)
    self.entryMoved(j)

  def entryMoved(self, i):
    """
    Call this after moving an element to update its position in the heap.
    This is to support decreaseKey()
    """
    self.array[i]._eheap_index_ = i
    
  def isValid(self):
    for i in range(1, len(self.array)-1):
      pi = self.indexParent(i)
      if self.array[i] < self.array[pi]:
        print(f'  isValid fail: [{i}]({self.array[i]}) < [{pi}]({self.array[pi]})')
        return False
    return True

  def print(self):
    for i, x in enumerate(self.array):
      print(f'{i:3d} {x}')


class HeapNode:
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return str(self.value)
  def __lt__(self, that):
    return self.value < that.value
  def __eq__(self, that):
    return self.value == that.value
  
def testHeap():
  import random

  input = [HeapNode(random.randint(0, 999)) for _ in range(100)]
  # input = [HeapNode(x) for x in [15, 38, 95, 24, 96, 22, 75, 23, 88, 17, 25, 1, 26, 14, 65, 90, 11, 10, 50, 81, 97, 72, 90]]

  sorted_input = input.copy()
  sorted_input.sort()
  input_str = '[' + ', '.join([str(x) for x in input]) + ']'
  print(f'input = {input_str}')

  print('heapify array')
  h = Heap(input)
  if not h.isValid():
    print(f'not valid, heap = {h.array!r}')
    return False

  # print(f'heaped array')
  # h.print()

  for i in range(len(input)):
    x = h.pop()
    if x != sorted_input[i]:
      print(f'Error i={i}, popped {x}, expected {sorted_input[i]}')
      return False
    h.isValid()
    assert len(h) == len(input) - i - 1

  print('add individual elements to heap')
  h = Heap()
  for x in input:
    h.add(x)
    if not h.isValid():
      print(f'Heap failed after adding {h.size()} entries, last one={x}')
      return False

  for i in range(len(input)):
    x = h.pop()
    if x != sorted_input[i]:
      print(f'Error i={i}, popped {x}, expected {sorted_input[i]}')
      return False
    h.isValid()
    assert len(h) == len(input) - i - 1

  print('decreaseKey test')
  h = Heap(input)
  for _ in range(len(input)):
    i = random.randint(0, len(input)-1)
    e = h.get(i)
    save_state = h.array.copy()
    prev = e.value
    e.value = random.randint(0, e.value)
    print(f'{prev} -> {e.value}')
    # if not h.isValid():
    #   print(f'  change heap[{i}] from {prev} to {e.value} invalidated heap')
    h.decreaseKey(i)
    if not h.isValid():
      print(f'  Error: calling decreaseKey left invalid heap')
      return False
    
    
  print('all good')

if __name__ == '__main__':
  testHeap()

  
