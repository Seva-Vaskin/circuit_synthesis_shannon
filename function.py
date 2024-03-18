class Function:
    def __init__(self, truth_table: str, name: str):
        self.truth_table = int(truth_table[::-1], 2)
        assert bin(len(truth_table)).count('1') == 1, "Function must have exactly one '1' in its binary representation"
        self.args_count = len(truth_table).bit_length() - 1
        assert str(self) == truth_table, f"Expected {truth_table}, got {str(self)} instead."
        self.name = name

    def __call__(self, *args) -> bool:
        assert isinstance(args, list) or isinstance(args, tuple)
        assert len(args) == self.args_count

        function_bit = 0
        for arg in args:
            function_bit = function_bit * 2 + arg
        return bool(self.truth_table >> function_bit & 1)

    def __str__(self) -> str:
        return format(self.truth_table, f"0{2 ** self.args_count}b")[::-1]


class Functions:
    NOT = Function("10", "NOT")
    AND = Function("0001", "AND")
    OR = Function("0111", "OR")
    NAND = Function("1110", "NAND")
    NOR = Function("1000", "NOR")
    XOR = Function("0110", "XOR")
    NXOR = Function("1001", "NXOR")
    ZERO = Function("00", "ZERO")
    ONE = Function("11", "ONE")
