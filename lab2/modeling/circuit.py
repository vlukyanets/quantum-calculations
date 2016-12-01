# 2016 (C) Valentin Lukyanets, SCSm-16-1


from line import Line
from pin import Pin
import weakref


class Circuit:
    def __init__(self, lines_count, input_lines_list, output_lines_list):
        self.truthtable_storage = {}
        self.lines = []
        for i in range(lines_count):
            self.lines.append(Line())
        self.input_lines = [self.lines[index] for index in input_lines_list]
        self.output_lines = [self.lines[index] for index in output_lines_list]
        self.elements = {}
        self.input_pins = []
        self.output_pins = []
        self.__elements_calculation_order = []

        for line in self.input_lines:
            pin = Pin(self, line)
            line.driver = weakref.ref(pin)
            self.input_pins.append(pin)

        for line in self.output_lines:
            pin = Pin(self, None)
            line.drivens.append(weakref.ref(pin))
            self.output_pins.append(pin)

    def get_line_by_index(self, index):
        return self.lines[index]

    def prepare(self):
        self.__elements_calculation_order = []
        element_linked_lines = {element_name: [] for element_name in self.elements}
        for line in self.lines:
            driver = line.driver()
            drivens = [driven() for driven in line.drivens]
            for driven in drivens:
                driver_element_name = driver.element().name
                driven_element_name = driven.element().name
                element_linked_lines[driven_element_name].append(driver_element_name)

        elements_visiting = {name: False for name in self.elements}
        rank = {name: -1 for name in self.elements}

        def calculate_rank(element, current_rank):
            if current_rank > rank[element.name]:
                return

            if elements_visiting[element.name]:
                return

            elements_visiting[element.name] = True
            rank[element.name] = current_rank
            for next_element in element_linked_lines:
                calculate_rank(next_element, current_rank + 1)
            elements_visiting[element.name] = False

        for line in self.output_lines:
            start_element = line.driver().element()
            calculate_rank(start_element, 1)

        maximal_rank = max(rank, key=rank.get)
        for element_name in rank:
            rank[element_name] = maximal_rank - rank[element_name] + 1

        for element_name in sorted(rank.items(), key=lambda (key, value): value):
            self.__elements_calculation_order.append(self.elements[element_name])

    def stimulate_by_vector(self, vector):
        for input_value, pin in zip(vector, self.input_pins):
            pin.value = input_value

        for line in self.input_lines:
            line.propagate()

        for element in self.__elements_calculation_order:
            element_input_values = [pin.value for pin in element.input_pins]
            element_output_values = element.truthtable[element_input_values]
            for pin, output_value in zip(element.output_pins, element_output_values):
                pin.value = output_value
                next_line = pin.line_drive() if pin.line_drive is not None else None
                if next_line:
                    next_line.propagate()