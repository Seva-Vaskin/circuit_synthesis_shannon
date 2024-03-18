from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Union, Optional
from function import Function


class Circuit:
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
        self.input_labels = input_labels
        self.label_to_identifier = dict()
        self.gates: List[Circuit.Gate] = list()
        for i, input_label in enumerate(input_labels):
            gate_id = self.make_gate(input_label)
            assert gate_id == i
        assert all(self.gates[i].identifier == i for i in range(len(input_labels)))
        self.output_identifiers = list()

    def unify_gate(self, gate: Union[str, int]) -> int:
        if isinstance(gate, str):
            gate = self.label_to_identifier[gate]
        assert isinstance(gate, int)
        return gate

    def tag_gate_as_output(self, gate: Optional[str, int]):
        gate = self.unify_gate(gate)
        self.output_identifiers.append(gate)

    def make_gate(self, label: str, gate_inputs: Optional[Union[Optional[int, str], ...]] = None,
                  function: Optional[Function] = None) -> int:

        identifier = self.gen_gate_identifier(label)
        if gate_inputs is not None:
            gate_inputs = list(map(self.unify_gate, gate_inputs))
            gate_args = list(map(lambda x: self.gates[x], gate_inputs))
        else:
            gate_args = None
        gate = Circuit.Gate(identifier, label, gate_args, function)
        self.gates.append(gate)
        return identifier

    def __getitem__(self, gate_identifier: Union[str, int]) -> Circuit.Gate:
        gate_identifier = self.unify_gate(gate_identifier)
        gate = self.gates[gate_identifier]
        return gate

    def gen_gate_identifier(self, label: str) -> int:
        assert label not in self.label_to_identifier.keys()
        identifier = len(self.label_to_identifier)
        self.label_to_identifier[label] = identifier
        return identifier

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
