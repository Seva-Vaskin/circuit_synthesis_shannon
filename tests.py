import math
import unittest
from typing import List
from itertools import product
from function import Functions

from circuit import Circuit
from circuit_synthesis import CircuitSynthesis
import random


class CircuitSynthesisTests(unittest.TestCase):

    def check_correctness(self, circuit: Circuit, truth_tables: List[str]):
        self.assertEqual(len(truth_tables), len(circuit.output_identifiers))
        evaluated_truth_tables = circuit.eval_all_truth_tables()
        actual_truth_tables = list(map(lambda x: evaluated_truth_tables[x], circuit.output_identifiers))
        expected_truth_tables = list(map(lambda x: list(map(lambda y: bool(int(y)), x)), truth_tables))
        self.assertListEqual(actual_truth_tables, expected_truth_tables)

    def check_synthesis(self, circuit: Circuit, truth_tables: List[str]):
        CircuitSynthesis.gen_simple_circuit(circuit, list(range(len(circuit.input_labels))), truth_tables)
        print(circuit)
        self.check_correctness(circuit, truth_tables)

    def check_shannen_synthesis(self, inputs_count: int, truth_tables: List[str], split_count: int,
                                check_correctness=True):
        circuit = Circuit([f"x{i}" for i in range(inputs_count)])
        CircuitSynthesis.shannen_algorithm(circuit, list(range(len(circuit.input_labels))), split_count, truth_tables)
        # print(circuit)
        ln = 0
        for x in circuit.gates:
            if x.function != Functions.NOT:
                ln += 1
        print(len(circuit.gates), ln)
        # print(circuit)
        if check_correctness:
            self.check_correctness(circuit, truth_tables)

    def test_simple_simple_shannen_synthesis(self):
        self.check_shannen_synthesis(3, ["11110011"], 1)

    def check_random_table_of_size_n_m(self, n, m):
        # self.assertFalse(True)
        random.seed(n * 10000 + m)
        truth_tables = [''.join(map(str, [random.randint(0, 1) for i in range(2 ** n)])) for j in range(m)]
        split_counter = n - int(math.log2(n))

        self.check_shannen_synthesis(n, truth_tables, split_counter, check_correctness=False)
        self.check_shannen_synthesis(n, truth_tables, split_counter + 1, check_correctness=False)

    def test_random_tables(self):
        for n, m in [(6, 1), (8, 1), (10, 1), (12, 1), (14, 1), (16, 1) ]:
            print(f"Test random with inputs={n} outputs={m}")
            self.check_random_table_of_size_n_m(n, m)

    def test_ex18(self):
        self.assertFalse(True)
        with open("exs/ex18.txt", "r") as f:
            truth_tables = list(f.read().split("\n"))
            n = int(math.log2(len(truth_tables[0])))
            # print(n)
            self.check_shannen_synthesis(n, truth_tables, n - 3)

    def test_ex66(self):
        self.assertFalse(True)
        with open("exs/ex66.txt", "r") as f:
            truth_tables = list(f.read().split("\n"))
            n = int(math.log2(len(truth_tables[0])))
            # print(n)
            c = Circuit([f"x{i}" for i in range(n)])
            self.check_shannen_synthesis(c, truth_tables, n - 3)
            # CircuitSynthesis.gen_simple_circuit(c, [i for i in range(n)], truth_tables)
            # print(len(c.gates))

    def test_simple_synthesis(self):
        self.check_shannen_synthesis(2, ["0011"], 1)

    def test_synthesis(self):
        self.check_shannen_synthesis(3, ["00110100"], 1)

    def test_synthesis_all_zeros(self):
        self.check_shannen_synthesis(3, ["00000000"], 1)

    def test_synthesis_multi(self):
        self.check_shannen_synthesis(3, ["00110100", "11101111", "01010101"], 1)

    def test_synthesis_one_one(self):
        self.check_shannen_synthesis(6, ["1000010000011100111001000001110010010100000111001000010000011100"], 4)


if __name__ == '__main__':
    unittest.main()
