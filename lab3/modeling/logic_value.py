# 2016 (C) Valentin Lukyanets, SCSm-16-1


class LogicValue:
    FALSE = 0
    TRUE = 1
    X = 2
    SAVE_VALUE = 3
    UNDEFINED = 4


class FaultModelingValue:
    NONE = 0
    TRUE = 1
    FALSE = 2
    X = 3
    UNDEFINED = 4


def fault_modeling_value_to_str(value):
    strings = {
        FaultModelingValue.NONE: '.',
        FaultModelingValue.FALSE: '0',
        FaultModelingValue.TRUE: '1',
        FaultModelingValue.X: 'X',
    }
    return strings.get(value, "")


def superposition(fault_value, logic_value):
    result = {
        (FaultModelingValue.NONE, LogicValue.FALSE): FaultModelingValue.X,
        (FaultModelingValue.NONE, LogicValue.TRUE): FaultModelingValue.X,
        (FaultModelingValue.TRUE, LogicValue.FALSE): FaultModelingValue.FALSE,
        (FaultModelingValue.TRUE, LogicValue.TRUE): FaultModelingValue.TRUE,
        (FaultModelingValue.FALSE, LogicValue.FALSE): FaultModelingValue.TRUE,
        (FaultModelingValue.FALSE, LogicValue.TRUE): FaultModelingValue.FALSE,
        (FaultModelingValue.X, LogicValue.FALSE): FaultModelingValue.NONE,
        (FaultModelingValue.X, LogicValue.TRUE): FaultModelingValue.X,
    }
    return result.get((fault_value, logic_value), FaultModelingValue.UNDEFINED)


def is_logic_value_allowed_as_truthtable_input(value):
    allowed_values = [LogicValue.FALSE, LogicValue.TRUE, LogicValue.X]
    return value in allowed_values


def invert(value):
    result_values = {
        LogicValue.FALSE: LogicValue.TRUE,
        LogicValue.TRUE: LogicValue.FALSE,
    }
    return result_values.get(value, value)


def logic_value_to_str(value):
    strings = {
        LogicValue.FALSE: '0',
        LogicValue.TRUE: '1',
        LogicValue.X: 'X',
        LogicValue.SAVE_VALUE: '+',
        LogicValue.UNDEFINED: 'U',
    }
    return strings.get(value, "")


def logic_value_from_str(s):
    values = {
        '0': LogicValue.FALSE,
        '1': LogicValue.TRUE,
        'X': LogicValue.X,
        '+': LogicValue.SAVE_VALUE,
    }
    return values.get(s, LogicValue.UNDEFINED)


def is_covered_by_line(input_terms, truthtable_line):
    for input_term, truthtable_line_term in zip(input_terms, truthtable_line):
        if not is_logic_value_allowed_as_truthtable_input(input_term):
            return False

        if truthtable_line_term in [LogicValue.X, input_term]:
            continue

        return False

    return True
