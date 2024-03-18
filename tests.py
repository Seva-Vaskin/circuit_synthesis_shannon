import unittest
from typing import List
from itertools import product

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

    def test_simple_synthesis(self):
        self.check_synthesis(Circuit(["x0", "x1"]), ["0011"])

    def test_synthesis(self):
        self.check_synthesis(Circuit(["x0", "x1", "x2"]), ["00110100"])

    def test_synthesis_all_zeros(self):
        self.check_synthesis(Circuit(["x0", "x1", "x2"]), ["00000000"])

    def test_synthesis_one_one(self):
        self.check_synthesis(Circuit(["x0", "x1", "x2", "x3"]), ["0000010000000000"])

    def test_synthesis_multi(self):
        self.check_synthesis(Circuit(["x0", "x1", "x2"]), ["00110100", "11101111", "01010101"])


if __name__ == '__main__':
    unittest.main()
