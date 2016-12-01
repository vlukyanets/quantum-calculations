# 2016 (C) Valentin Lukyanets, SCSm-16-1


from logic_value import is_logic_value_allowed_as_truthtable_input, logic_value_to_str, is_covered_by_line


class TruthtableLine:
    def __init__(self, input_terms, output_terms):
        self.input_terms = input_terms
        self.output_terms = output_terms


class Truthtable:
    def __init__(self, name, inputs, outputs):
        self.name = name
        self.truthtable_lines = []
        self.inputs = inputs
        self.outputs = outputs

    def __add__(self, line):
        for term in line.input_terms:
            if not is_logic_value_allowed_as_truthtable_input(term):
                raise Exception("Value {} is not allowed as input in truthtable".format(logic_value_to_str(term)))

        self.truthtable_lines.append(line)

    def __getitem__(self, key):
        for line in self.truthtable_lines:
            if is_covered_by_line(key, line.input_terms):
                return line.output_terms

        return None
