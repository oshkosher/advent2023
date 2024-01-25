#!/usr/bin/env python3

"""
Advent of Code 2023, day 20: Pulse Propagation

Simulate a circuit, then monitor the right gates to reduce
it to a least common multiple problem.

Ed Karrels, ed.karrels@gmail.com, January 2024
"""

import sys, re, collections, time, math
from collections import deque, namedtuple


button_press_idx = 0
is_complete = False

"""
Data structures

A single queue manages pulses.
Each pulse is lo(0) or hi(1) and knows its destination gate.
There is a list of all gates.
  Or a map, keyed by name?
  Maybe that too, but the order needs to be consistent for the state
  computation to work consistently.
Each gate has a reference to the gate receiving its output, and if
the destination gate is a NAND the index of this input.
Flip-flop gates remember their current output.
NAND gates remember their most recent inputs.
"""

class Circuit:
  def __init__(self):
    self.gate_map = {}
    self.gate_list = []
    self.state_bit_offsets = None
    self.broadcaster = BroadcastGate()
    self.pulse_q = deque()
    self.button_presses = 0
    self.pulse_count = [0, 0]

  def initStateCompute(self):
    """
    Call this after all gates gave been initialized.
    """
    self.state_bit_offsets = []
    b = 0
    for gate in self.gate_list:
      self.state_bit_offsets.append(b)
      b += gate.stateSize()

  def getState(self):
    s = 0
    for gate, offset in zip(self.gate_list, self.state_bit_offsets):
      s |= gate.state() << offset
    return s

  def pressButton(self):
    """
    Send a low pulse to add broadcaster outputs.
    """
    # pulse_q.append(Pulse(value, og.gate, og.input_idx))

    # print(f'button press {self.button_presses} button -low-> broadcaster')
    self.button_presses += 1
    self.broadcaster.outputPulse(0, self.pulse_q)
    self.pulse_count[0] += 1

    # propagate pulses
    while len(self.pulse_q) > 0:
      pulse = self.pulse_q.popleft()
      self.pulse_count[pulse.value] += 1
      # print(f'{pulse.src_gate.name} -{["low","high"][pulse.value]}-> {pulse.dest_gate}')
      pulse.dest_gate.input(pulse.value, pulse.input_idx, self.pulse_q)

    
class Pulse:
  def __init__(self, src_gate, value, dest_gate, input_idx):
    self.src_gate = src_gate
    self.value = value
    self.dest_gate = dest_gate
    self.input_idx = input_idx


class OutputWire:
  def __init__(self, dest_gate, input_idx):
    self.dest_gate = dest_gate
    # which of that gate's inputs I'm wired
    self.input_idx = input_idx


GATE_BCAST = 0
GATE_OUTPUT = 1
GATE_FF = 2
GATE_NAND = 3
    
class Gate:
  def __init__(self, name):
    self.name = name
    # OutputWire objects
    self.output_list = []

    # call this when the value changes to 1
    self.monitor_fn = None

  def type(self):
    # GATE_FF or GATE_NAND
    return None

  def __str__(self):
    return self.name
  
  def addInput(self, input_gate):
    """
    Sets this gate as one of my inputs and returns the index of the input
    line to which it is wired.
    """
    return 0

  def addOutput(self, gate):
    """
    Connect another gate to my output.
    """
    idx = gate.addInput(self)
    self.output_list.append(OutputWire(gate, idx))

  def stateSize(self):
    """
    Number of bits in my state.
    """
    return 0

  def state(self):
    """
    Return this gate's state as an integer [0..2**stateSize)
    """
    return 0

  def input(self, value, input_idx, pulse_q):
    """
    Process an input pulse.
    """
    pass

  def outputPulse(self, value, pulse_q):
    """
    Process an output pulse.
    """
    global button_press_idx

    if self.monitor_fn and value==1:
      # print(f'  {self.name}->{value} on press {button_press_idx}')
      self.monitor_fn(self, button_press_idx)
      
    for og in self.output_list:
      pulse_q.append(Pulse(self, value, og.dest_gate, og.input_idx))


class BroadcastGate(Gate):
  def __init__(self):
    Gate.__init__(self, 'broadcaster')

  def type(self):
    return GATE_BCAST
  
  def input(self, value, input_idx, pulse_q):
    self.outputPulse(value, pulse_q)


class OutputGate(Gate):
  def __init__(self, name):
    Gate.__init__(self, name)
    self.lo_count = 0
    self.hi_count = 0

  def type(self):
    return GATE_OUTPUT
  
  def input(self, value, input_idx, pulse_q):
    # print(f'  output {value}')
    if value == 0:
      self.lo_count += 1
    else:
      self.hi_count += 1

  
class FlipFlopGate(Gate):
  def __init__(self, name):
    Gate.__init__(self, name)
    self.value = 0

  def type(self):
    return GATE_FF

  def addInput(self, gate):
    return 0

  def stateSize(self):
    return 1

  def state(self):
    return self.value

  def input(self, value, input_idx, pulse_q):
    if value == 1: return

    self.value = 1 - self.value
    self.outputPulse(self.value, pulse_q)
    
  
class NANDGate(Gate):
  def __init__(self, name):
    Gate.__init__(self, name)
    self.input_gates = []
    self.input_bits = 0
    # bit mask of 1's for all inputs = 2**(len(input_gates))-1
    self.mask = 0

  def type(self):
    return GATE_NAND

  def addInput(self, gate):
    self.input_gates.append(gate)
    self.mask = 2*self.mask + 1
    return len(self.input_gates)-1

  def stateSize(self):
    return len(self.input_gates)

  def state(self):
    return self.input_bits

  def input(self, value, input_idx, pulse_q):
    bit = 1 << input_idx
    if value:
      self.input_bits |= bit
    else:
      self.input_bits = self.input_bits & (self.mask - bit)

    result = 0 if self.input_bits == self.mask else 1

    self.outputPulse(result, pulse_q)


def readInput(inf):
  # returns Circuit
  c = Circuit()

  # gate name -> list of output names
  output_lists = {}
  
  for line in inf:
    words = line.split()
    assert words[1]=='->'
    outs = [s.replace(',', '') for s in words[2:]]

    if words[0] == 'broadcaster':
      name = words[0]
      gate = c.broadcaster
    else:
      name = words[0][1:]
      if words[0][0] == '%':
        gate = FlipFlopGate(name)
      else:
        assert words[0][0] == '&'
        gate = NANDGate(name)

    output_lists[name] = outs
    c.gate_map[name] = gate
    c.gate_list.append(gate)


  for name, outs in output_lists.items():
    gate = c.gate_map[name]
    for out_name in outs:
      out_gate = c.gate_map.get(out_name, None)
      if not out_gate:
        out_gate = OutputGate(out_name)
        c.gate_map[out_name] = out_gate
        c.gate_list.append(out_gate)
      gate.addOutput(out_gate)

  c.initStateCompute()
  
  return c


def part1(filename):
  with open(filename) as inf:
    circuit = readInput(inf)

  # print(f'state = {circuit.getState()}')
  for i in range(1000):
    circuit.pressButton()
    # print(f'state = {circuit.getState()}')

    # print(f'output {circuit.output.lo_count} lo, {circuit.output.hi_count} hi, prod = {circuit.output.lo_count * circuit.output.hi_count}')

  pulse_count_prod = circuit.pulse_count[0] * circuit.pulse_count[1]
  # print(f'pulses handled: {circuit.pulse_count!r}, product = {pulse_count_prod}')
  print(f'part1 {pulse_count_prod}')


def inputsOf(dest_gate, circuit):
  inputs = set()
  for gate in circuit.gate_list:
    for wire in gate.output_list:
      if wire.dest_gate == dest_gate:
        inputs.add(gate)
  return inputs


def writeGraph(filename):
  """
  Write the circuit to an output file that can be used as input for GraphViz,
  to make it easier to visualize the circuit.
  FYI, to use GraphViz from the command line:
    fdp -Tpdf -oday20.pdf day20.gv

  Here's a really nice animation
  https://anceps.net/advent/circuit.php
  """
  with open(filename) as inf:
    circuit = readInput(inf)

  sys.stderr.write('to process with GraphViz:\n  fdp -Tpdf -oday20.pdf day20.gv\n')
    
  print('digraph day20 {')

  for gate in circuit.gate_list:
    shape = 'oval'
    if gate.type() == GATE_FF: shape = 'box'
    if gate.type() == GATE_NAND: shape = 'circle'

    color = 'black'
    if gate.name == 'broadcaster':
      color='blue'
    elif gate.name == 'rx':
      color='red'
    
    print(f'  {gate.name} [shape={shape}, color={color}]')
    
    for out in gate.output_list:
      print(f'  {gate.name} -> {out.dest_gate}')

  print('}')

  
def part2(filename):
  global button_press_idx, is_complete

  with open(filename) as inf:
    circuit = readInput(inf)
  rx_gate = circuit.gate_map['rx']

  # monitor the inputs of the inputs of rx
  rx_inputs = inputsOf(rx_gate, circuit)
  # print(f'rx inputs: {" ".join([g.name for g in rx_inputs])}')
  key_gates = {}
  for rx_in in rx_inputs:
    for gate in inputsOf(rx_in, circuit):
      key_gates[gate] = None

  # print(f'key_gates = {" ".join([str(k) for k in key_gates.keys()])}')

  keys_complete = 0
  def keyGateMonitor(gate, cycle_count):
    """
    This is a callback which will be called when one of the key gates is activated.
    Store the cycle_count, and return True if we're all done.
    """
    global is_complete
    nonlocal keys_complete
    if key_gates[gate] == None:
      key_gates[gate] = cycle_count
      keys_complete += 1
      if keys_complete == len(key_gates):
        is_complete = True
  
  for k in key_gates:
    k.monitor_fn = keyGateMonitor
    # print(f'monitor {k.name}')
  
  while not is_complete:
    button_press_idx += 1
    circuit.pressButton()

  cycle_counts = []
  for gate, cycle_count in key_gates.items():
    # print(f'{gate} {cycle_count}')
    cycle_counts.append(cycle_count)

  lcm = math.lcm(*cycle_counts)
  print(f'part2 {lcm}')

  
if __name__ == '__main__':
  filename = 'day20.in.txt'
  if len(sys.argv) > 1:
    filename = sys.argv[1]
  # writeGraph(filename)
  part1(filename)
  part2(filename)
