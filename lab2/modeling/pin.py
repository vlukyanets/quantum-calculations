# 2016 (C) Valentin Lukyanets, SCSm-16-1


import weakref
from logic_value import LogicValue


class Pin:
    def __init__(self, element, line_drive):
        self.element = weakref.ref(element)
        self.line_drive = weakref.ref(line_drive) if line_drive else None
        self.value = LogicValue.FALSE
