#!/usr/bin/env python
# encoding=UTF-8

"""
生成CTR训练数据
支持GBDT/LIBSVM 2种输出格式
GBDT格式: Init label weight feature
LIBSVM格式: label feature
输入数据格式(2): feature,label
"""

import sys
from optparse import OptionParser

FORMAT_GBDT = "gbdt"
FORMAT_LIBSVM = "libsvm"

parser = OptionParser()
parser.add_option("-o", "--instance_format", dest="instance_format", help="instance format[gbdt|libsvm]")

(options, args) = parser.parse_args()

# 输出格式
if options.instance_format:
    ins_format = options.instance_format
    if ins_format != FORMAT_GBDT and ins_format != FORMAT_LIBSVM:
        print "parameter instance_format error"
        parser.print_help()
        sys.exit(1)
else:
    ins_format = FORMAT_GBDT

for line in sys.stdin:
    cols = line.strip("\n\r").split("\t")
    if len(cols) == 2:
        feature = cols[0]
        label = cols[1]
        if ins_format == FORMAT_GBDT:
            print "%s %s %d %s" % ("0.0", label, 1, feature)
        elif ins_format == FORMAT_LIBSVM:
            print "%s %s" % (label, feature)
        else:
            print >> sys.stderr, "reporter:counter:My Stat,Reduce Format Error,1"
            continue
    else:
        print >> sys.stderr, "reporter:counter:My Stat,Reduce Length Error,1"

