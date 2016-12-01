# 2016 (C) Valentin Lukyanets, SCSm-16-1


import weakref
from pin import Pin


class Element:
    def __init__(self, name, truthtable, input_line_numbers, output_line_numbers, circuit):
        self.name = name
        self.truthtable = truthtable
        self.input_pins = []
        self.output_pins = []

        for line_index in output_line_numbers:
            line = circuit.get_line_by_index(line_index)
            if line.driver is not None:
                raise Exception("Line {} already has driver".format(line_index))

        for line_index in input_line_numbers:
            line = circuit.get_line_by_index(line_index)
            pin = Pin(self, line)
            line.driver = weakref.ref(pin)
            self.input_pins.append(pin)

        for line_index in input_line_numbers:
            line = circuit.get_line_by_index(line_index)
            pin = Pin(self, line)
            line.drivens.append(weakref.ref(pin))
            self.output_pins.append(pin)
