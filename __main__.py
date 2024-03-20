import sys
import math
import unittest
from typing import List
from itertools import product
from function import Functions

from circuit import Circuit
from circuit_synthesis import CircuitSynthesis


def main():
    file_in = sys.argv[1]
    file_out = sys.argv[2]
    f = open(file_in, "r")
    truth_tables = list(f.read().split("\n"))
    if truth_tables[-1] == "":
        truth_tables.pop()
    n = int(math.log2(len(truth_tables[0])))
    c = Circuit([f"x{i}" for i in range(n)])
    k = [0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5, 5, 5]
    CircuitSynthesis.shannen_algorithm(c, [i for i in range(n)], n - k[n], truth_tables)
    f.close()
    f2 = open(file_out, "w")
    f2.write(str(c))
    f2.close()


if __name__ == "__main__":
    main()
