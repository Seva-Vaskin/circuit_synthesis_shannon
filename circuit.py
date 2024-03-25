from __future__ import annotations

import copy
import sys
from dataclasses import dataclass
from typing import List, Tuple, Union, Optional, Iterable, Set
from function import Function
from itertools import product
from collections import deque


class Circuit:
    GateTag = Union[str, int]
    GateTags = Iterable[GateTag]

    @dataclass
    class Gate:
        identifier: int
        label: str
        args: Optional[Tuple[Circuit.Gate]] = None
        function: Optional[Function] = None

        def __str__(self):
            if self.args is None:
                assert self.function is None
                return f"INPUT({self.label})"
            assert self.function is not None
            return f"{self.label}={self.function.name}({', '.join(map(lambda x: x.label, self.args))})"

    def __init__(self, input_labels: List[str]):
        self.input_labels = copy.deepcopy(input_labels)
        self.label_to_identifier = dict()
        self.gates: List[Circuit.Gate] = list()
        for i, input_label in enumerate(input_labels):
            gate_id = self.make_gate(input_label)
            assert gate_id == i
        assert all(self.gates[i].identifier == i for i in range(len(input_labels)))
        self.output_identifiers: List[int] = list()
        self.trash_variables_count = 0

    def unify_gate(self, gate: GateTag) -> int:
        assert isinstance(gate, str) or isinstance(gate, int)
        if isinstance(gate, str):
            gate = self.label_to_identifier[gate]
        assert isinstance(gate, int)
        return gate

    def tag_gate_as_output(self, gate: GateTag):
        gate = self.unify_gate(gate)
        self.output_identifiers.append(gate)

    def make_gate(self, label: str, input_gates: Optional[GateTags] = None,
                  function: Optional[Function] = None) -> int:
        identifier = self.gen_gate_identifier(label)
        if input_gates is not None:
            input_gates = list(map(self.unify_gate, input_gates))
            gate_args = list(map(lambda x: self.gates[x], input_gates))
        else:
            gate_args = None
        gate = Circuit.Gate(identifier, label, gate_args, function)
        self.gates.append(gate)
        return identifier

    def create_gate_alias(self, gate: GateTag, alias: str):
        assert alias not in self.label_to_identifier
        gate = self.unify_gate(gate)
        self.label_to_identifier[alias] = gate

    def __getitem__(self, gate_tag: GateTag) -> Circuit.Gate:
        gate_tag = self.unify_gate(gate_tag)
        gate = self.gates[gate_tag]
        return gate

    def gen_gate_identifier(self, label: str) -> int:
        assert label not in self.label_to_identifier.keys()
        identifier = len(self.gates)
        self.label_to_identifier[label] = identifier
        return identifier

    def gen_trash_label(self) -> str:
        self.trash_variables_count += 1
        return f"__trash_{self.trash_variables_count - 1}"

    def __str__(self):
        res = []
        for gate in self.gates:
            res.append(str(gate))
        res += list(map(lambda x: f"OUTPUT({self.gates[x].label})", self.output_identifiers))
        return '\n'.join(res)

    def __call__(self, args: str) -> List[bool]:
        assert len(args) == len(self.input_labels)
        gate_vals = list(map(lambda x: bool(int(x)), args))
        for i in range(len(args), len(self.gates)):
            gate = self.gates[i]
            assert gate.args is not None
            args_values = list(map(lambda x: gate_vals[x.identifier], gate.args))
            gate_val = gate.function(*args_values)
            gate_vals.append(gate_val)
        return list(map(lambda x: gate_vals[x], self.output_identifiers))

    def eval_all_truth_tables(self) -> List[List[bool]]:
        input_gates = [self.unify_gate(g) for g in self.input_labels]
        assert set(input_gates) == set(range(len(self.input_labels)))
        truth_tables: List[List[bool]] = [list() for i in range(len(self.gates))]
        for input_config in product([False, True], repeat=len(input_gates)):
            for i, val in enumerate(input_config):
                truth_tables[i].append(val)
        for gate_id in range(len(self.input_labels), len(self.gates)):
            gate = self.gates[gate_id]
            gate_inputs = map(lambda x: x.identifier, gate.args)
            input_truth_tables = map(lambda x: truth_tables[x], gate_inputs)
            input_sets = zip(*input_truth_tables)

            truth_tables[gate_id] = list(map(lambda input_set: gate.function(*input_set), input_sets))
        return truth_tables

    def find_used_gates(self) -> Set[int]:
        q = deque()
        used: Set[int] = set()
        for output in self.output_identifiers:
            q.append(output)
            used.add(output)
        while q:
            gate_id = q.popleft()
            gate = self.gates[gate_id]
            if gate.args is None:
                continue
            for next_gates in gate.args:
                next_id = next_gates.identifier
                if next_id in used:
                    continue
                used.add(next_id)
                q.append(next_id)
        return used

    def delete_unused_gates(self) -> Circuit:
        used_gates = list(sorted(self.find_used_gates()))
        id_mapping = dict(map(lambda x: (x[1], x[0]), enumerate(used_gates)))
        circuit = Circuit(self.input_labels)
        for gate_id in sorted(used_gates):
            gate = self.gates[gate_id]
            if gate.args is None:
                assert gate.label in self.input_labels
                continue
            arg_identifiers = list(map(lambda x: id_mapping[x.identifier], gate.args))
            circuit.make_gate(gate.label, arg_identifiers, gate.function)
        for output in self.output_identifiers:
            circuit.tag_gate_as_output(id_mapping[output])
        return circuit
