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

import os
import imp
import argparse
import tabulate

i = imp.find_module("mallet", [".."])
imp.load_module("mallet", *i)
import mallet.class_dump as class_dump


_whitespace = "\u200b"


def normalize_type(type_32bit, type_64bit):
    if type_32bit is None:
        type_32bit = type_64bit
    elif type_64bit is None:
        type_64bit = type_32bit

    if type_32bit == type_64bit:
        if type_32bit == "struct CGPoint":
            return "CGPoint"
        elif type_32bit == "struct CGSize":
            return "CGSize"
        elif type_32bit == "struct CGRect":
            return "CGRect"
        elif type_32bit == "struct UIEdgeInsets":
            return "UIEdgeInsets"
        elif type_32bit == "struct __CFDictionary *":
            return "NSDictionary *"
        elif type_32bit == "struct _NSRange":
            return "NSRange"
        return type_32bit
    elif type_32bit == "BOOL" and type_64bit == "bool":
        return "BOOL"
    elif type_32bit == "char" and type_64bit == "_Bool":
        return "BOOL"
    elif type_32bit == "int" and type_64bit == "long long":
        return "NSInteger"
    elif type_32bit == "long" and type_64bit == "long long":
        return "NSInteger"
    elif type_32bit == "unsigned int" and type_64bit == "unsigned long long":
        return "NSUInteger"
    elif type_32bit == "unsigned long" and type_64bit == "unsigned long long":
        return "NSUInteger"
    elif type_32bit == "float" and type_64bit == "double":
        return "CGFloat"
    elif type_32bit == "struct CADoublePoint" and type_64bit == "struct CGPoint":
        return "CADoublePoint"

    print(("Different types: {} != {}".format(type_32bit, type_64bit)))
    return type_64bit


def dump_class(module_name, class_name):
    """
    Prints class description.

    :param str module_name: Module name.
    :param str class_name: Class name.
    """
    # Current directory path.
    current_dir = os.path.abspath(__file__)
    current_dir, _ = os.path.split(current_dir)
    input_dir = os.path.join(current_dir, "../mallet/{}/{}".format(module_name, class_dump.class_dumps_folder_name))
    input_dir = os.path.normpath(input_dir)

    m = class_dump.Module(module_name, input_dir)
    architectures = ["armv7", "i386", "arm64", "x86_64"]
    main_architecture = "arm64"
    architecture_32bit = "armv7"
    architecture_64bit = "arm64"
    classes = [m.get_class_or_load(a, class_name) for a in architectures]
    main_class = m.get_class_or_load(main_architecture, class_name)

    # Output.
    output = "Class: {}\n".format(class_name)
    if main_class.super_class_name:
        output += "Super class: {}\n".format(main_class.super_class_name)
    if main_class.protocols:
        output += "Protocols: {}\n".format(", ".join(main_class.protocols))

    # iVars.
    ivars = sorted(main_class.ivars, key=lambda x: x.offset, reverse=True)
    if ivars:
        # Headers
        headers = ["Name"]
        [headers.append(a) for a in architectures]

        rows = list()
        for ivar in ivars:
            # iVars for all architectures.
            architecture_ivars = [cl.get_ivar(ivar.name) for cl in classes]
            architecture_ivar_32bit = architecture_ivars[architectures.index(architecture_32bit)]
            architecture_ivar_64bit = architecture_ivars[architectures.index(architecture_64bit)]

            # Normalized type name.
            type32 = architecture_ivar_32bit.ivarType if architecture_ivar_32bit else None
            type64 = architecture_ivar_64bit.ivarType if architecture_ivar_64bit else None
            type_name = normalize_type(type32, type64)
            splitted_type_name = type_name.split("\n")

            # For multiline types add "empty" rows.
            ivar_rows = list()
            for type_line in splitted_type_name[:-1]:
                type_row = [type_line.replace(" ", _whitespace)] + [""] * len(architectures)
                ivar_rows.append(type_row)

            # Add type line.
            type_row = ["{} {}".format(splitted_type_name[-1], ivar.name).replace(" ", _whitespace)]
            for architecture_ivar in architecture_ivars:
                value = "{0:>3} 0x{0:03X} / {1:<2}".format(architecture_ivar.offset if architecture_ivar is not None else -1,
                                                            architecture_ivar.size if architecture_ivar is not None else None).replace(" ", _whitespace)
                type_row.append(value)

            ivar_rows.append(type_row)
            ivar_rows.reverse()  # Ivars are reversed, so rows for ivar also have to be reversed.
            rows.extend(ivar_rows)

        rows.reverse()
        output += tabulate.tabulate(rows, headers)

    print(output)


if __name__ == "__main__":
    # Argument parser.
    parser = argparse.ArgumentParser(description="Prints class description.")
    parser.add_argument("module")
    parser.add_argument("class")

    # Parse arguments.
    args = parser.parse_args()
    class_name = vars(args)["class"]
    module_name = args.module

    dump_class(module_name, class_name)
