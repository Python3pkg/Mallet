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

import functools
import lldb
import lldb.formatters
import objc_runtime
import logging
import LLDBLogger

Architecture_unknown = 0
Architecture_armv7 = 1
Architecture_armv7s = 1
Architecture_arm64 = 2
Architecture_i386 = 3
Architecture_x86_64 = 4


def architecture_name_from_target(target):
    """
    Return architecture name from given LLDB target.

    :param lldb.SBTarget target: LLDB target.
    :return: Architecture name or None if cannot find architecture.
    :rtype: str | None
    """
    triple = target.GetTriple()
    """:type : str"""

    if triple.startswith("i386"):
        return "i386"
    elif triple.startswith("x86_64"):
        return "x86_64"
    elif triple.startswith("armv7"):
        return "armv7"
    elif triple.startswith("armv7s"):
        return "armv7s"
    elif triple.startswith("arm64"):
        return "arm64"

    return None


def architecture_type_from_name(architecture_name):
    """
    Returns architecture type from name.

    :param str architecture_name: Architecture name
    :return: Architecture type.
    :rtype: int
    """
    architecture = Architecture_unknown

    if architecture_name == "i386":
        architecture = Architecture_i386
    elif architecture_name == "x86_64":
        architecture = Architecture_x86_64
    elif architecture_name == "armv7":
        architecture = Architecture_armv7
    elif architecture_name == "armv7s":
        architecture = Architecture_armv7s
    elif architecture_name == "arm64":
        architecture = Architecture_arm64

    return architecture


def architecture_type_from_target(target):
    """
    Returns architecture name from target.

    :param lldb.SBTarget target: LLDB target
    :return: Architecture name.
    :rtype: str
    """
    architecture_name = architecture_name_from_target(target)
    return architecture_type_from_name(architecture_name)


def is_64bit_architecture(architecture):
    """
    Returns True if target architecture is 64 bit.

    :param int architecture: Architecture type.
    :return: True if architecture is 64 bit.
    :rtype: bool
    """
    if architecture == Architecture_unknown:
        return False
    if architecture == Architecture_x86_64 or architecture == Architecture_arm64:
        return True
    return False


def is_64bit_architecture_from_name(architecture_name):
    """
    Returns True if target architecture is 64 bit.

    :param str architecture_name: Architecture name.
    :return: True if architecture is 64 bit.
    :rtype: bool
    """
    architecture = architecture_type_from_name(architecture_name)
    return is_64bit_architecture(architecture)


def is_64bit_architecture_from_target(target):
    """
    Returns True if target architecture is 64 bit.

    :param lldb.SBTarget target: Architecture name.
    :return: True if architecture is 64 bit.
    :rtype: bool
    """
    architecture = architecture_type_from_target(target)
    return is_64bit_architecture(architecture)


# Statistics for objc_runtime.
statistics = lldb.formatters.metrics.Metrics()
statistics.add_metric("invalid_isa")
statistics.add_metric("invalid_pointer")
statistics.add_metric("unknown_class")
statistics.add_metric("code_notrun")


def get_class_data(value_obj):
    """
    Get class_data and wrapper.

    :param lldb.SBValue value_obj:
    :return: Wrapper and class data.
    """
    global statistics
    class_data, wrapper = objc_runtime.Utilities.prepare_class_detection(value_obj, statistics)
    return class_data, wrapper


def generic_summary_provider(value_obj, internal_dict, class_synthetic_provider, supported_classes=[]):
    """
    Checks value type and returns summary.

    :param lldb.SBValue value_obj:
    :param dict internal_dict:
    :param class class_synthetic_provider:
    :param dict[str] supported_classes:
    :return: Value summary.
    :rtype: str
    """
    # Class data.
    logger = logging.getLogger(__name__)
    type_name = value_obj.GetTypeName() if value_obj.GetTypeName() else "Unknown type name"
    class_data, wrapper = get_class_data(value_obj)

    # Class data invalid.
    # if not class_data.is_valid():
    #     logger.debug("generic_summary_provider: class_data invalid for \"{}\".".format(type_name))
    #     return ""

    # Not supported class.
    if len(supported_classes) > 0 and class_data.class_name() not in supported_classes:
        logger.debug("generic_summary_provider: not supported class \"{}\" in {}.".format(type_name, supported_classes))
        return ""

    # Using wrapper if available.
    # if wrapper is not None:
    #     logger.debug("generic_summary_provider: using wrapper for \"{}\".".format(type_name))
    #     return wrapper.message()

    # Using Class Summary Provider.
    wrapper = class_synthetic_provider(value_obj, internal_dict)
    if wrapper is not None:
        # logger.debug("generic_summary_provider: using summary provider {} for \"{}\"."
        #                               .format(class_synthetic_provider, type_name))
        return wrapper.summary()

    # Summary not available.
    # logger.debug("generic_summary_provider: summary unavailable")
    return "Summary Unavailable"


class save_parameter(object):
    """
    Decorator. Saves method return value to object parameter.

    :param str _param_name: Name of parameter.
    """
    def __init__(self, param_name):
        """
        :param str param_name: Name of parameter.
        """
        super(save_parameter, self).__init__()
        self._param_name = param_name

    def __call__(self, func):
        """
        Returns method wrapper for method "func".

        :param function func: Wrapped function.
        :return: Method wrapper.
        """
        def decorator(s, *args, **kwargs):
            """
            Checks if method has attribute with given name. If not raise AttributeError exception.
            If parameter has value returns it, if not execute method and save value to parameter.

            :param object s: Object / self.
            :param args: Arguments.
            :param kwargs: Arguments.
            :return: Value.
            :raise AttributeError: If object doesn't have given attribute.
            """
            logger = logging.getLogger(__name__)
            # Check if "cache" parameter exists.
            if not hasattr(s, self._param_name):
                # logger.error("SaveParam.save_parameter.wrapper: no attribute with name: \"{}\"".
                #                               format(self._param_name if self._param_name else "No parameter name"))
                raise AttributeError
            # Get cached value.
            value = getattr(s, self._param_name)
            # Execute method to cache value.
            if value is None:
                # logger.debug("SaveParam.save_parameter.wrapper: na value for: \"{}\"".format(self._param_name))
                value = func(s, *args, **kwargs)
                setattr(s, self._param_name, value)
            # else:
            #     logger.debug("SaveParam.save_parameter.wrapper: using value: \"{}\" for param: \"{}\"".
            #                                   format(value, self._param_name))
            return value
        return decorator
