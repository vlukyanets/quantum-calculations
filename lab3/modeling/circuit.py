# 2016 (C) Valentin Lukyanets, SCSm-16-1


from logic_value import LogicValue, invert, FaultModelingValue, superposition
from line import Line
from pin import Pin
import weakref
import operator


class Circuit:
    def __init__(self, lines_count, input_lines_list, output_lines_list, assert_lines_list):
        self.lines_count = lines_count
        self.truthtable_storage = {}
        self.lines = []
        for i in range(self.lines_count):
            self.lines.append(Line(i))
        self.input_lines = [self.lines[index] for index in input_lines_list]
        self.output_lines = [self.lines[index] for index in output_lines_list]
        self.assert_lines = [self.lines[index] for index in assert_lines_list]
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
        element_linked_lines[''] = []
        for line in self.lines:
            driver = line.driver()
            drivens = [driven() for driven in line.drivens]
            for driven in drivens:
                driver_element_name = driver.element().name if hasattr(driver.element(), 'name') else ''
                driven_element_name = driven.element().name if hasattr(driven.element(), 'name') else ''
                element_linked_lines[driven_element_name].append(driver_element_name)

        elements_visiting = {name: False for name in self.elements}
        rank = {name: -1 for name in self.elements}

        def calculate_rank(element, current_rank):
            if not hasattr(element, 'name'):
                return

            if current_rank < rank[element.name]:
                return

            if elements_visiting[element.name]:
                return

            elements_visiting[element.name] = True
            rank[element.name] = current_rank
            for next_element_name in element_linked_lines[element.name]:
                calculate_rank(self.elements.get(next_element_name), current_rank + 1)
            elements_visiting[element.name] = False

        for line in self.output_lines:
            start_element = line.driver().element()
            calculate_rank(start_element, 1)

        maximal_rank = max(rank.values())
        for element_name in rank:
            rank[element_name] = maximal_rank - rank[element_name] + 1

        sorted_ranks = sorted(rank.items(), key=operator.itemgetter(1))
        for element_name, _ in sorted_ranks:
            self.__elements_calculation_order.append(self.elements[element_name])

    def stimulate_by_vector(self, vector):
        for input_value, pin in zip(vector, self.input_pins):
            pin.value = input_value

        for line in self.input_lines:
            line.propagate()

        for element in self.__elements_calculation_order:
            element_input_values = [pin.value for pin in element.input_pins]
            element_output_values = element.truthtable[element_input_values]
            if element_output_values is None:
                element_output_values = [LogicValue.UNDEFINED] * len(element.output_pins)
            for pin, output_value in zip(element.output_pins, element_output_values):
                if output_value != LogicValue.SAVE_VALUE:
                    pin.value = output_value
                    next_line = pin.line_drive() if pin.line_drive is not None else None
                    if next_line:
                        next_line.propagate()

    def check_fault(self, line_idx):
        checked_faults = []
        fault_line = self.get_line_by_index(line_idx)
        for driven_ref in fault_line.drivens:
            driven = driven_ref().element()
            if isinstance(driven, Circuit):
                checked_faults.append(invert(fault_line.value))
                continue

            truthtable = driven.truthtable
            input_lines = [pin.line_drive() for pin in driven.input_pins]
            original_input = [line.value for line in input_lines]
            fault_input = [line.value if line is not fault_line else invert(line.value) for line in input_lines]
            original_result, fault_result = truthtable[original_input], truthtable[fault_input]
            if original_result != fault_result:
                checked_faults.append(invert(fault_line.value))

        if LogicValue.FALSE in checked_faults:
            if LogicValue.TRUE in checked_faults:
                return FaultModelingValue.X
            else:
                return FaultModelingValue.FALSE
        else:
            if LogicValue.TRUE in checked_faults:
                return FaultModelingValue.TRUE
            else:
                return FaultModelingValue.NONE

    def get_available_lines(self, start_line_index):
        all_available_lines = [start_line_index]
        all_available_lines_index = 0
        while 1:
            if all_available_lines_index >= len(all_available_lines):
                break

            element = self.get_line_by_index(all_available_lines[all_available_lines_index]).driver().element()
            if not isinstance(element, Circuit):
                for input_pin in element.input_pins:
                    all_available_lines.append(input_pin.line_drive().index)
            all_available_lines_index += 1

        return [LogicValue.TRUE if i in all_available_lines else LogicValue.FALSE for i in range(self.lines_count)]

    def modeling_faults(self, vectors, assertions):
        result_faults = []
        assertion_lines_avail = [self.get_available_lines(assertion_line.index)
                                 for assertion_line in self.assert_lines]
        faults = []
        for vector, assertion in zip(vectors, assertions):
            self.stimulate_by_vector(vector)
            faults.append([self.check_fault(line_idx) for line_idx in range(self.lines_count)])

        activation_matrix = [[LogicValue.UNDEFINED for i in range(self.lines_count)] for j in range(len(vectors))]
        for i in range(len(vectors)):
            for line_idx in range(self.lines_count):
                count = 0
                for j, assertion_line_idx in enumerate(self.assert_lines):
                    if (assertions[i][j] == LogicValue.FALSE and
                            assertions[i][j] != assertion_lines_avail[j][line_idx]):
                        count = 0
                        break

                    if (assertions[i][j] == LogicValue.FALSE and
                            assertion_lines_avail[j][line_idx] == LogicValue.FALSE):
                        continue

                    if (assertions[i][j] == LogicValue.TRUE and
                            assertion_lines_avail[j][line_idx] == LogicValue.TRUE):
                        count += 1

                activation_matrix[i][line_idx] = LogicValue.TRUE if count > 0 else LogicValue.FALSE

        func_matrix = [[FaultModelingValue.UNDEFINED for i in range(self.lines_count)] for j in range(len(vectors))]
        for i in range(len(vectors)):
            for line_idx in range(self.lines_count):
                func_matrix[i][line_idx] = superposition(faults[i][line_idx], activation_matrix[i][line_idx])

        for line_idx in range(self.lines_count):
            first_digit_ones, second_digit_ones = 0, 0
            for i in range(len(vectors)):
                fault_value = func_matrix[i][line_idx]
                if fault_value == FaultModelingValue.FALSE:
                    first_digit_ones += 1
                elif fault_value == FaultModelingValue.TRUE:
                    second_digit_ones += 1
                elif fault_value == FaultModelingValue.X:
                    first_digit_ones += 1
                    second_digit_ones += 1

            if (first_digit_ones == len(vectors)) and (second_digit_ones == len(vectors)):
                result_value = FaultModelingValue.X
            elif first_digit_ones == len(vectors):
                result_value = FaultModelingValue.FALSE
            elif second_digit_ones == len(vectors):
                result_value = FaultModelingValue.TRUE
            else:
                result_value = FaultModelingValue.NONE

            if result_value != FaultModelingValue.NONE:
                result_faults.append([line_idx, result_value])

        return faults, assertion_lines_avail, activation_matrix, func_matrix, result_faults
