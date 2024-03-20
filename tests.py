import math
import unittest
from typing import List
from itertools import product
from function import Functions

from circuit import Circuit
from circuit_synthesis import CircuitSynthesis


class CircuitSynthesisTests(unittest.TestCase):

    def check_correctness(self, circuit: Circuit, truth_tables: List[str]):
        self.assertEqual(len(truth_tables), len(circuit.output_identifiers))
        for args in map(lambda x: ''.join(x), product("01", repeat=len(circuit.input_labels))):
            res = circuit(args)
            self.assertEqual(len(res), len(circuit.output_identifiers))
            idx = int(args, 2)
            for i, r in enumerate(res):
                self.assertEqual(str(int(r)), truth_tables[i][idx])

    def check_synthesis(self, circuit: Circuit, truth_tables: List[str]):
        CircuitSynthesis.gen_simple_circuit(circuit, list(range(len(circuit.input_labels))), truth_tables)
        print(circuit)
        self.check_correctness(circuit, truth_tables)

    def check_shannen_synthesis(self, circuit: Circuit, truth_tables: List[str], split_count: int):
        CircuitSynthesis.shannen_algorithm(circuit, list(range(len(circuit.input_labels))), split_count, truth_tables)
        #print(circuit)
        ln = 0
        for x in circuit.gates:
            if x.function != Functions.NOT:
                ln += 1
        print(len(circuit.gates), ln)
        self.check_correctness(circuit, truth_tables)

    def test_simple_simple_shannen_synthesis(self):
        self.check_shannen_synthesis(Circuit(["x0", "x1", "x2"]), ["11110011"], 1)

    def test_ex18(self):
        f = open("ex18.txt", "r")
        truth_tables = list(f.read().split("\n"))
        n = int(math.log2(len(truth_tables[0])))
        #print(n)
        c = Circuit([f"x{i}" for i in range(n)])
        self.check_shannen_synthesis(c, truth_tables, n - 3)
        f.close()

    def test_ex66(self):
        f = open("ex66.txt", "r")
        truth_tables = list(f.read().split("\n"))
        n = int(math.log2(len(truth_tables[0])))
        #print(n)
        c = Circuit([f"x{i}" for i in range(n)])
        self.check_shannen_synthesis(c, truth_tables, n - 4)
        f.close()

    def test_simple_synthesis(self):
        self.check_shannen_synthesis(Circuit(["x0", "x1"]), ["0011"], 1)

    def test_synthesis(self):
        self.check_shannen_synthesis(Circuit(["x0", "x1", "x2"]), ["00110100"], 1)

    def test_synthesis_all_zeros(self):
        self.check_shannen_synthesis(Circuit(["x0", "x1", "x2"]), ["00000000"], 1)


    def test_synthesis_multi(self):
        self.check_shannen_synthesis(Circuit(["x0", "x1", "x2"]), ["00110100", "11101111", "01010101"], 1)

    def test_synthesis_one_one(self):
        self.check_shannen_synthesis(Circuit(["x0", "x1", "x2", "x3", "x4", "x5"]), ["1000010000011100111001000001110010010100000111001000010000011100"], 3)



if __name__ == '__main__':
    unittest.main()
