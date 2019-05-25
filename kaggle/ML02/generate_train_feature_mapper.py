#!/usr/bin/env python
# encoding=UTF-8

"""
生成训练数据
支持CTR/CVR
支持特征选择
支持紧密和稀疏2种特征格式

输入数据格式(24): 

key: feature
"""
import os
import sys
from optparse import OptionParser

FORMAT_DENSE = 0  # 紧密
FORMAT_SPARSE = 1  # 稀疏
DATA_TYPE_CTR = "ctr"
DATA_TYPE_CVR = "cvr"
MISSING_VALUE = "-70000.0"
DOUBLESTR="1.7976931348623157E308"
INFINITY="Infinity"
NAN="NaN"

MAYBE_UNKNOWN={}
MAYBE_UNKNOWN["DISTANCE"] = 1
MAYBE_UNKNOWN["ADISTANCE"] = 1
MAYBE_UNKNOWN["CTR"] = 1
MAYBE_UNKNOWN["CXR"] = 1
MAYBE_UNKNOWN["CVR"] = 1
MAYBE_UNKNOWN["RCTR"] = 1
MAYBE_UNKNOWN["RCXR"] = 1


LABEL_NEG = "0"
LABEL_POS = "1"


class Transfer(object):
    def __init__(self, file_select_feature):
        self._select_feature_file = file_select_feature
        self._load_select_feature()

    def _load_select_feature(self):
        self._selected_features = []
        for row in open(self._select_feature_file, 'r'):
            self._selected_features.append(row.strip())

    def transform(self, features_s, format_out):
        if format_out == FORMAT_DENSE:
            return self.transform_to_dense(features_s)
        elif format_out == FORMAT_SPARSE:
            return self.transform_to_sparse(features_s)
        else:
            return "-1"

    def transform_to_dense(self, features_s):
        feature_values = {}
        feats = features_s.split(",")
        for feat_s in feats:
            try:
                feat, v = feat_s.split(":")
                if v == DOUBLESTR or v == INFINITY or v == NAN or v== MISSING_VALUE:
                    continue
                feature_values[feat] = v
            except ValueError:
                continue
        value_list = []
        index = -1
        for feat in self._selected_features:
            index += 1
            try:
                value = feature_values[feat]
                if feat == "DISTANCE" or feat == "ADISTANCE":
                    if float(value) > 3.0E6:
                        continue
                value_list.append("%d:%s" % (index, value))
            except KeyError:
                if not MAYBE_UNKNOWN.has_key(feat):
                    value_list.append("%d:%s" % (index, "0.0"))
                continue
        value_str = " ".join(value_list)
        return value_str

    def transform_to_sparse(self, features_s):
        feature_values = {}
        feats = features_s.split(",")
        for feat_s in feats:
            try:
                feat, v = feat_s.split(":")
                if v == DOUBLESTR or v == INFINITY or v == NAN:
                    continue
                feature_values[feat] = v
            except ValueError:
                continue
        value_list = []
        index = -1
        for feat in self._selected_features:
            index += 1
            try:
                value = feature_values[feat]
                if feat == "DISTANCE" or feat == "ADISTANCE":
                    if float(value) > 3.0E6:
                        value = MISSING_VALUE
            except KeyError:
                if MAYBE_UNKNOWN.has_key(feat):
                    value = MISSING_VALUE
                else:
                    value = "-1"
            value_list.append("%d:%s" % (index, value))
            #value_list.append(value)
        value_str = " ".join(value_list)
        return value_str


parser = OptionParser()
parser.add_option("-d", "--data_type", dest="data_type", help="data type [ctr|cvr]")
parser.add_option("-f", "--file", dest="feature_file", help="select feature file")
parser.add_option("-t", "--feature_format", dest="feature_format", type="int", help="feature format [0|1]")

(options, args) = parser.parse_args()

# 数据类型
if options.data_type:
    data_type = options.data_type
    if data_type != DATA_TYPE_CTR and data_type != DATA_TYPE_CVR:
        print "parameter data_type error"
        parser.print_help()
        sys.exit(1)
else:
    data_type = DATA_TYPE_CTR

# 特征文件
if not options.feature_file:
    parser.print_help()
    sys.exit(1)
if not os.path.isfile(options.feature_file):
    print "select_feature_file error"
    parser.print_help()
    sys.exit(1)

# 特征格式
if options.feature_format:
    feat_format = options.feature_format
    if feat_format != FORMAT_DENSE and feat_format != FORMAT_SPARSE:
        print "parameter feature_format error"
        parser.print_help()
        sys.exit(1)
else:
    feat_format = FORMAT_DENSE
    #feat_format = FORMAT_SPARSE

transfer = Transfer(options.feature_file)

pos_num = 0
neg_num = 0

for line in sys.stdin:
    line = line.strip("\n\r")
    cols = line.split("\t")
    if len(cols) == 24:
        feature_str = cols[23]
        # global_id = cols[15]
        clicked = cols[0]
        ordered = cols[1]
        try:
            feature_vector = transfer.transform(feature_str, feat_format)
        except:
            print >> sys.stderr, "reporter:counter:My Stat,Map Feature_str,1"
            continue
        if feature_vector == "":
            print >> sys.stderr, "reporter:counter:My Stat,Map Feature Empty,1"
            continue
        if data_type == DATA_TYPE_CTR:
            label = clicked
        elif data_type == DATA_TYPE_CVR:
            label = ordered
        if label == LABEL_NEG:
            neg_num += 1
        elif label == LABEL_POS:
            pos_num += 1
        else:
            print >> sys.stderr, "reporter:counter:My Stat,Map Label Error,1"
            continue
        print "%s\t%s" % (feature_vector, label)
        print >> sys.stderr, "reporter:counter:My Stat,Map OK,1"
    else:
        print >> sys.stderr, "reporter:counter:My Stat,Map Length Error,1"

print >> sys.stderr, "reporter:counter:My Stat,Map Pos Num,%d" % pos_num
print >> sys.stderr, "reporter:counter:My Stat,Map Neg Num,%d" % neg_num

