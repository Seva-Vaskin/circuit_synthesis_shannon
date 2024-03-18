from typing import List
from circuit import Circuit
from itertools import product
from function import Functions


def label_dis(i, j):
    return f"dis_{i}_{j}"


def label_gate(pref, i):
    return f"{pref}_{i}"


def label_not(pref, i):
    return f"{pref}_n_{i}"


def label_f(pref, truth_table):
    return f"{pref}_f_{truth_table}"


class CircuitSynthesis:

    @staticmethod
    def gen_all_conjunctions(circuit: Circuit, gates: List[int]):

        n = len(gates)
        if n == 1:
            circuit.make_gate(f"{pref}_0", (gates[0],), Functions.BUFF)
            circuit.make_gate(f"{pref}_1", (gates[0],), Functions.NOT)
            return

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

            circuit.make_gate(label_dis(0, j), (label_gate(pref, where_ones[0]), label_gate(pref, where_ones[1])),
                              Functions.OR)
            for i in range(2, len(where_ones)):
                circuit.make_gate(label_dis(i - 1, j),
                                  (f"{pref}_{where_ones[i]}", label_dis(i - 2, j)),
                                  Functions.OR)
            circuit.tag_gate_as_output(label_dis(len(where_ones) - 2, j))

    @staticmethod
    def gen_all_functions(circuit: Circuit, input_gates: List[int], pref: str):
        if len(input_gates) == 1:
            for truth_table, func in [("01", Functions.BUFF), ("10", Functions.NOT), ("00", Functions.ZERO),
                                      ("11", Functions.ONE)]:
                circuit.make_gate(label_f(pref, truth_table), tuple([input_gates[0]]), func)
        else:
            CircuitSynthesis.gen_all_functions(circuit, input_gates[1:], pref)

            for truth_table_0, truth_table_1 in product(
                    map(lambda x: ''.join(x), product("01", repeat=2 ** (len(input_gates) - 1))),
                    repeat=2):
                truth_table = truth_table_0 + truth_table_1
                f_0_label, f_1_label, inp_not_label = [circuit.gen_trash_label() for _ in range(3)]
                circuit.make_gate(f_1_label, (input_gates[0], label_f(pref, truth_table_1)), Functions.AND)

                circuit.make_gate(inp_not_label, tuple([input_gates[0]]), Functions.NOT)
                circuit.make_gate(f_0_label, (inp_not_label, label_f(pref, truth_table_0)), Functions.AND)

                circuit.make_gate(label_f(pref, truth_table), (f_0_label, f_1_label), Functions.OR)

    @staticmethod
    def shannen_algorithm(circuit: Circuit, input_labels: List[int], split_count, truth_tables: List[str]):
        conj_pref = "c"
        all_func_pref = "a"
        assert split_count < len(input_labels)
        CircuitSynthesis.gen_all_conjunctions(circuit, input_labels[:split_count], conj_pref)
        CircuitSynthesis.gen_all_functions(circuit, input_labels[split_count:], all_func_pref)

        for i, truth_table in enumerate(truth_tables):
            prev_label = None
            block_len = 2 ** (len(input_labels) - split_count)
            for x in map(lambda xx: ''.join(xx), product("01", repeat=split_count)):
                int_x = int(x, 2)
                not_x = ''.join('0' if i == '1' else '0' for i in x)
                block_truth_table = truth_table[block_len * int_x:block_len * (int_x + 1)]

                and_gate_label = circuit.gen_trash_label()
                and_gate = circuit.make_gate(and_gate_label,
                                             (f"{conj_pref}_{not_x}", label_f(all_func_pref, block_truth_table)),
                                             Functions.AND)
                if prev_label is not None:
                    or_gate_label = circuit.gen_trash_label()
                    or_gate = circuit.make_gate(or_gate_label, (and_gate, prev_label), Functions.OR)
                    prev_label = or_gate
                else:
                    prev_label = and_gate

            circuit.tag_gate_as_output(prev_label)
