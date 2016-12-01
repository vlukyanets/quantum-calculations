# 2016 (C) Valentin Lukyanets, SCSm-16-1


class LogicValue:
    FALSE = 0
    TRUE = 1
    X = 2
    SAVE_VALUE = 3
    UNDEFINED = 4


def is_logic_value_allowed_as_truthtable_input(value):
    allowed_values = [LogicValue.FALSE, LogicValue.TRUE, LogicValue.X]
    return value in allowed_values


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
