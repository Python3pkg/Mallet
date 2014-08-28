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
import lldb
import LLDBLogger


class TypeCache(object):
    def __init__(self):
        super(TypeCache, self).__init__()
        self.types = dict()
        self._populated = False

    @staticmethod
    def _get_type_from_name(type_name, target):
        """
        Returns type (SBType) from target (SBTarget) based on type name.
        """
        if isinstance(type_name, unicode):
            type_name = type_name.encode('utf-8')
        is_pointer = type_name.endswith("*")
        only_type_name = type_name.rstrip("*").strip()
        t = target.FindFirstType(only_type_name)
        if is_pointer:
            t = t.GetPointerType()

        return t

    def get_type(self, type_name, target):
        # Validate data.
        if type_name is None or target is None:
            return None

        # Populate type cache with standard types.
        self._populate_standard_types(target)

        # Find and return type from cache.
        if type_name in self.types:
            return self.types[type_name]

        # Get type from name.
        LLDBLogger.get_logger().debug("Adding type {} to cache.".format(type_name))
        t = self._get_type_from_name(type_name, target)
        self.types[type_name] = t
        return t

    def _populate_standard_types(self, target):
        # Do not populate if already data was populated.
        if self._populated:
            return

        self._populated = True
        is64bit = Helpers.is_64bit_architecture_from_target(target)
        # LLDBLogger.get_logger().debug("Populating type cache.")

        # char, unsigned char
        self.types["char"] = target.GetBasicType(lldb.eBasicTypeChar)
        self.types["unsigned char"] = target.GetBasicType(lldb.eBasicTypeUnsignedChar)
        self.types["short"] = target.GetBasicType(lldb.eBasicTypeShort)
        self.types["unsigned short"] = target.GetBasicType(lldb.eBasicTypeUnsignedShort)
        self.types["int"] = target.GetBasicType(lldb.eBasicTypeInt)
        self.types["unsigned int"] = target.GetBasicType(lldb.eBasicTypeUnsignedInt)
        self.types["long"] = target.GetBasicType(lldb.eBasicTypeLong)
        self.types["unsigned long"] = target.GetBasicType(lldb.eBasicTypeUnsignedLong)
        self.types["long long"] = target.GetBasicType(lldb.eBasicTypeLongLong)
        self.types["unsigned long long"] = target.GetBasicType(lldb.eBasicTypeUnsignedLongLong)
        self.types["float"] = target.GetBasicType(lldb.eBasicTypeFloat)
        self.types["double"] = target.GetBasicType(lldb.eBasicTypeDouble)
        self.types["uuid_t"] = target.GetBasicType(lldb.eBasicTypeUnsignedInt128)
        self.types["id"] = target.GetBasicType(lldb.eBasicTypeObjCID)

        if is64bit:
            self.types["NSInteger"] = target.GetBasicType(lldb.eBasicTypeLong)
            self.types["NSUInteger"] = target.GetBasicType(lldb.eBasicTypeUnsignedLong)
            self.types["CGFloat"] = target.GetBasicType(lldb.eBasicTypeDouble)
            self.types["addr_type"] = target.GetBasicType(lldb.eBasicTypeUnsignedLongLong)
        else:
            self.types["NSInteger"] = target.GetBasicType(lldb.eBasicTypeInt)
            self.types["NSUInteger"] = target.GetBasicType(lldb.eBasicTypeUnsignedInt)
            self.types["CGFloat"] = target.GetBasicType(lldb.eBasicTypeFloat)
            self.types["addr_type"] = target.GetBasicType(lldb.eBasicTypeUnsignedLong)

        self.types["addr_ptr_type"] = self.types["addr_type"].GetPointerType()
        self.types["CGPoint"] = target.FindFirstType("CGPoint")
        self.types["CGSize"] = target.FindFirstType("CGSize")
        self.types["CGRect"] = target.FindFirstType("CGRect")
        self.types["UIEdgeInsets"] = target.FindFirstType("UIEdgeInsets")
        self.types["UIOffset"] = target.FindFirstType("UIOffset")
        self.types["struct CGPoint"] = target.FindFirstType("CGPoint")
        self.types["struct CGSize"] = target.FindFirstType("CGSize")
        self.types["struct CGRect"] = target.FindFirstType("CGRect")
        self.types["struct UIEdgeInsets"] = target.FindFirstType("UIEdgeInsets")
        self.types["struct UIOffset"] = target.FindFirstType("UIOffset")

        self.types["NSString *"] = target.FindFirstType("NSString").GetPointerType()
        self.types["NSAttributedString *"] = target.FindFirstType("NSAttributedString").GetPointerType()
        self.types["NSMutableAttributedString *"] = target.FindFirstType("NSMutableAttributedString").GetPointerType()
        self.types["NSNumber *"] = target.FindFirstType("NSNumber").GetPointerType()
        self.types["NSDecimalNumber *"] = target.FindFirstType("NSDecimalNumber").GetPointerType()
        self.types["NSURL *"] = target.FindFirstType("NSURL").GetPointerType()
        self.types["NSDate *"] = target.FindFirstType("NSDate").GetPointerType()
        self.types["NSData *"] = target.FindFirstType("NSData").GetPointerType()
        self.types["NSArray *"] = target.FindFirstType("NSArray").GetPointerType()
        self.types["NSMutableArray *"] = target.FindFirstType("NSMutableArray").GetPointerType()
        self.types["NSSet *"] = target.FindFirstType("NSSet").GetPointerType()
        self.types["NSDictionary *"] = target.FindFirstType("NSDictionary").GetPointerType()


def get_type_cache():
    if not hasattr(get_type_cache, "type_cache"):
        # LLDBLogger.get_logger().debug("Creating shared TypeCache.")
        get_type_cache.type_cache = TypeCache()
    return get_type_cache.type_cache
