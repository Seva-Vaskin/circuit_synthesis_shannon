from typing import List
from circuit import Circuit
from itertools import product
from function import Functions


def label_dis(i, j):
    return f"dis{i}_{j}"


def label_y(i):
    return f"y{i}"


class CircuitSynthesis:

    @staticmethod
    def gen_all_conjunctions(circuit: Circuit, gates: List[int]):

        n = len(gates)
        assert n > 1, "длина хотя бы 2"

        for ind in gates:
            circuit.make_gate("n" + str(ind), tuple([ind]), Functions.NOT)

        circuit.make_gate("y00", (gates[0], gates[1]), Functions.AND)
        circuit.make_gate("y01", (gates[0], "n" + str(gates[1])), Functions.AND)
        circuit.make_gate("y10", ("n" + str(gates[0]), gates[1]), Functions.AND)
        circuit.make_gate("y11", ("n" + str(gates[0]), "n" + str(gates[1])), Functions.AND)

        for i in range(2, n):
            for x in map(lambda prod: ''.join(prod), product("01", repeat=i)):
                circuit.make_gate("y" + x + "0", ("y" + x, gates[i]), Functions.AND)
                circuit.make_gate("y" + x + "1", ("y" + x, "n" + str(gates[i])), Functions.AND)

    @staticmethod
    def gen_simple_circuit(circuit: Circuit, input_gates: List[int], truth_tables: List[str]):
        n = len(input_gates)
        CircuitSynthesis.gen_all_conjunctions(circuit, input_gates)
        for j in range(len(truth_tables)):
            truth_table = truth_tables[j]
            assert len(truth_table) == 2 ** n, "таблица истинности и количество входов не соответствуют друг другу"
            where_ones = []
            for x in map(lambda prod: ''.join(prod), product("01", repeat=n)):
                if truth_table[2 ** n - int(x, 2) - 1] == "1":
                    where_ones.append(x)

            if len(where_ones) == 0:
                circuit.make_gate("ZERO", tuple([input_gates[0]]), Functions.ZERO)
                circuit.tag_gate_as_output("ZERO")
                continue
            if len(where_ones) == 1:
                circuit.tag_gate_as_output("y" + str(where_ones[0]))
                continue

            circuit.make_gate(label_dis(0, j), (label_y(where_ones[0]), label_y(where_ones[1])), Functions.OR)
            for i in range(2, len(where_ones)):
                circuit.make_gate(label_dis(i - 1, j),
                                  ("y" + where_ones[i], label_dis(i - 2, j)),
                                  Functions.OR)
            circuit.tag_gate_as_output(label_dis(len(where_ones) - 2, j))
