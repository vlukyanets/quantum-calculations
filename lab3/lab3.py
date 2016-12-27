#!/usr/bin/env python
# 2016 (C) Valentin Lukyanets, SCSm-16-1


from __future__ import print_function
import argparse
import re
import modeling


def read_input_data(filename):
    scheme_re = re.compile(r'^Scheme: (\d+) lines; input (\S+); output (\S+); assert (\S+)', re.IGNORECASE)
    truthtable_header_re = re.compile(r'^Truthtable "(.+)": (\d+) inputs, (\d+) outputs, (\d+) lines', re.IGNORECASE)
    truthtable_line_re = re.compile(r'^(\S+) (\S+)')
    element_re = re.compile(r'^Element "(.+)": "(.+)"; in (\S+); out (\S+)', re.IGNORECASE)
    vectors_re = re.compile(r'^Vectors: (\S+)', re.IGNORECASE)

    f = open(filename, "r")
    circuit = None
    vectors = []
    assertions = []
    truthtable = None
    inside_truthtable = False
    lines_left = 0
    for line in f:
        match = scheme_re.search(line)
        if match and not inside_truthtable:
            lines_count, inputs, outputs, asserts = int(match.group(1)), match.group(2), match.group(3), match.group(4)
            input_lines = [int(x) for x in inputs.split(",")]
            output_lines = [int(x) for x in outputs.split(",")]
            assert_lines = [int(x) for x in asserts.split(",")]

            circuit = modeling.Circuit(lines_count, input_lines, output_lines, assert_lines)
            continue

        match = element_re.search(line)
        if match and not inside_truthtable:
            element_name, truthtable_name, inputs, outputs = [match.group(i + 1) for i in range(4)]
            truthtable = circuit.truthtable_storage[truthtable_name]
            input_lines = [int(x) for x in inputs.split(",")]
            output_lines = [int(x) for x in outputs.split(",")]
            element = modeling.Element(element_name, truthtable, input_lines, output_lines, circuit)
            circuit.elements[element_name] = element
            continue

        match = vectors_re.search(line)
        if match and not inside_truthtable:
            vectors_str = match.group(1)
            vectors_str_list = vectors_str.split(";")
            vectors = [[modeling.logic_value_from_str(c) for c in s.split(",")[0]] for s in vectors_str_list]
            assertions = [[modeling.logic_value_from_str(c) for c in s.split(",")[1]] for s in vectors_str_list]
            continue

        match = truthtable_header_re.search(line)
        if match and not inside_truthtable:
            name = match.group(1)
            inputs, outputs, lines = [int(match.group(i + 2)) for i in range(3)]
            truthtable = modeling.Truthtable(name, inputs, outputs)
            lines_left = lines
            inside_truthtable = True
            continue

        match = truthtable_line_re.search(line)
        if match and inside_truthtable:
            input_terms_str, output_terms_str = match.group(1), match.group(2)
            input_terms = [modeling.logic_value_from_str(s) for s in input_terms_str]
            output_terms = [modeling.logic_value_from_str(s) for s in output_terms_str]
            truthtable += modeling.TruthtableLine(input_terms, output_terms)
            lines_left -= 1
            if lines_left == 0:
                inside_truthtable = False
                circuit.truthtable_storage[truthtable.name] = truthtable
            continue

    f.close()
    return circuit, vectors, assertions


def print_faults(f, tests, assertions_lines_count, assertions, faults, assertion_lines_avail,
                 activation_matrix, func_matrix, result_faults):
    print("Faults table", file=f)
    for test in range(tests):
        out1 = "".join([modeling.fault_modeling_value_to_str(value) for value in faults[test]])
        out2 = "".join([modeling.logic_value_to_str(value) for value in assertions[test]])
        out = " ".join([out1, out2])
        print(out, file=f)

    print("Assertion lines", file=f)
    for i in range(assertions_lines_count):
        out = "".join([modeling.logic_value_to_str(value) for value in assertion_lines_avail[i]])
        print(out, file=f)

    print("Activation matrix", file=f)
    for i in range(tests):
        out = "".join([modeling.logic_value_to_str(value) for value in activation_matrix[i]])
        print(out, file=f)

    print("Functional matrix", file=f)
    for i in range(tests):
        out = "".join([modeling.fault_modeling_value_to_str(value) for value in func_matrix[i]])
        print(out, file=f)

    print("Detected faults", file=f)
    out = ", ".join(['{}-{}'.format(fault[0], modeling.fault_modeling_value_to_str(fault[1]))
                     for fault in result_faults])
    print(out, file=f)


def main():
    parser = argparse.ArgumentParser(description="Modeling of circuits")
    parser.add_argument("-i", "--input", metavar="inputfile", type=str, help="Input file name")
    parser.add_argument("-o", "--output", metavar="outputfile", type=str, help="Output file name")
    args = parser.parse_args()
    input_filename = args.input
    output_filename = args.output

    circuit, vectors, assertions = read_input_data(input_filename)
    circuit.prepare()

    try:
        f = open(output_filename, "w")
        faults, assertion_lines_avail, activation_matrix, func_matrix, result_faults =\
            circuit.modeling_faults(vectors, assertions)
        print_faults(f, len(vectors), len(circuit.assert_lines), assertions, faults,
                     assertion_lines_avail, activation_matrix, func_matrix, result_faults)
        f.close()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
else:
    print("This module shouldn't be imported!")
