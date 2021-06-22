# -*- coding: utf-8 -*-
# @Time    : 2021/3/11 15:51
# @Author  : cosmo
# @Project : jinyan_python
# @File    : convert_to_simplified_chinese.py

from pathlib import Path
from tokenization import Tokenizer


class MyTokenizer(Tokenizer):
    def __init__(self):
        super().__init__()

    def simple_preprocess(self, sen:str)->str:
        # preprocess input text in a simple way
        sen = self.lower_letter(sen)
        sen = self.chinese_tradition2simplified(sen)
        sen = self.strQ2B(sen)  # 全角转半角
        sen = sen.replace(' ', '')
        return sen


sd_words_path = Path(r"E:\AI_data\jinyan_python\new_keywords\国务院词汇2021\remain_sd_keywords_2020_clean.txt")
sd_words_format_path = Path(r"E:\AI_data\jinyan_python\new_keywords\国务院词汇2021\remain_sd_keywords_2020_format.txt")
words = sd_words_path.read_text(encoding='utf-8').split('\n')

# convert
tokenizer = MyTokenizer()
clean_words = [tokenizer.simple_preprocess(_) for _ in words if _.strip()]
sd_words_format_path.write_text(data='\n'.join(clean_words), encoding='utf-8')


