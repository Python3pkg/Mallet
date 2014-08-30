#! /usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Bartosz Janda
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import Helpers
import UIControl


class UIDatePicker_SynthProvider(UIControl.UIControl_SynthProvider):
    # Class: UIDatePicker
    # Super class: UIControl
    # Protocols: UIPickerViewScrollTesting, NSCoding
    # Name:                                  armv7                 i386                  arm64                 x86_64
    # _UIDatePickerView * _pickerView    120 (0x078) / 4       120 (0x078) / 4       224 (0x0E0) / 8       224 (0x0E0) / 8
    # BOOL _useCurrentDateDuringDecoding 124 (0x07C) / 1       124 (0x07C) / 1       232 (0x0E8) / 1       232 (0x0E8) / 1

    def __init__(self, value_obj, internal_dict):
        super(UIDatePicker_SynthProvider, self).__init__(value_obj, internal_dict)
        self.type_name = "UIDatePicker"

        self.picker_view = None

    def get_picker_view(self):
        if self.picker_view:
            return self.picker_view

        self.picker_view = self.get_child_value("_pickerView")
        return self.picker_view

    def summary(self):
        picker_view = self.get_picker_view()
        picker_view_summary = picker_view.GetSummary()

        return picker_view_summary


def UIDatePicker_SummaryProvider(value_obj, internal_dict):
    return Helpers.generic_summary_provider(value_obj, internal_dict, UIDatePicker_SynthProvider)


def __lldb_init_module(debugger, dict):
    debugger.HandleCommand("type summary add -F UIDatePicker.UIDatePicker_SummaryProvider \
                            --category UIKit \
                            UIDatePicker")
    debugger.HandleCommand("type category enable UIKit")
