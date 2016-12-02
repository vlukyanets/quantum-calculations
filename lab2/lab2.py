#!/usr/bin/env python
# 2016 (C) Valentin Lukyanets, SCSm-16-1


from __future__ import print_function
import argparse
import re
import modeling


def read_input_data(filename):
    scheme_re = re.compile(r'^Scheme: (\d+) lines; input (\S+); output (\S+)', re.IGNORECASE)
    truthtable_header_re = re.compile(r'^Truthtable "(.+)": (\d+) inputs, (\d+) outputs, (\d+) lines', re.IGNORECASE)
    truthtable_line_re = re.compile(r'^(\S+) (\S+)')
    element_re = re.compile(r'^Element "(.+)": "(.+)"; in (\S+); out (\S+)', re.IGNORECASE)
    vectors_re = re.compile(r'^Vectors: (\S+)', re.IGNORECASE)

    f = open(filename, "r")
    circuit = None
    stimulating_vectors = []
    truthtable = None
    inside_truthtable = False
    lines_left = 0
    for line in f:
        match = scheme_re.search(line)
        if match and not inside_truthtable:
            lines_count, inputs, outputs = int(match.group(1)), match.group(2), match.group(3)
            input_lines = [int(x) for x in inputs.split(",")]
            output_lines = [int(x) for x in outputs.split(",")]

            circuit = modeling.Circuit(lines_count, input_lines, output_lines)
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
            stimulating_vectors = [[modeling.logic_value_from_str(c) for c in s] for s in vectors_str.split(",")]
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
    return circuit, stimulating_vectors


def print_all_lines(f, circuit):
    out = ''.join([modeling.logic_value_to_str(line.value) for line in circuit.lines])
    print(out, file=f)


def main():
    parser = argparse.ArgumentParser(description="Modeling of circuits")
    parser.add_argument("-i", "--input", metavar="inputfile", type=str, help="Input file name")
    parser.add_argument("-o", "--output", metavar="outputfile", type=str, help="Output file name")
    args = parser.parse_args()
    input_filename = args.input
    output_filename = args.output

    circuit, stimulating_vectors = read_input_data(input_filename)
    circuit.prepare()

    try:
        f = open(output_filename, "w")
        for vector in stimulating_vectors:
            circuit.stimulate_by_vector(vector)
            print_all_lines(f, circuit)
        f.close()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
else:
    print("This module shouldn't be imported!")
