# -*- coding: utf-8 -*-
"""
Created on 2020/11/25 11:30

@author: cosmo

关键词表分拣
"""

import os

from basic_text_preprocess import Preprocessor






if __name__ == '__main__':
    new_words_path = r"E:\AI_data\jinyan_python\doc\文件-敏感词-黄敏.txt"
    exists_words_path = r"E:\AI_data\jinyan_python\doc\newest_sensitive_words"
    dst_path = r"E:\AI_data\jinyan_python\doc\剩余敏感词.txt"

    processor1 = Preprocessor(load_sep='|')
    processor2 = Preprocessor()
    new_words = processor1.load_text(new_words_path)
    exists_words = processor2._union_load(exists_words_path)
    rest_words = processor2._diff_set(new_words, exists_words)
    processor2.dump_text(rest_words, dst_path)
