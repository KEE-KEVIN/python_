# -*- coding: utf-8 -*-
# @Time    : 2021/3/11 14:14
# @Author  : cosmo
# @Project : jinyan_python
# @File    : sensitive_words_deduplicate.py

import fileinput
from pathlib import Path

exist_keywords_path = Path(r"E:\AI_data\jinyan_python\new_keywords\最新关键词210310")
state_department_keywords_path = Path(
    r"E:\AI_data\jinyan_python\new_keywords\国务院词汇2021\state_department_keywords_2020.txt")
remain_sd_keywords_path = Path(
    r"E:\AI_data\jinyan_python\new_keywords\国务院词汇2021\remain_sd_keywords_2020.txt")

state_department_keywords = state_department_keywords_path.read_text(encoding='utf-8').split('\n')
state_department_keywords = [_.strip() for _ in state_department_keywords if _.strip()]
print(f"len of state department words:{len(state_department_keywords)}, head5:{state_department_keywords[:5]}")

exist_paths = list(exist_keywords_path.glob('./**/*.txt'))
with fileinput.input(files=exist_paths, openhook=fileinput.hook_encoded(encoding='utf-8')) as file:
    exist_keywords = []
    for line in file:
        line = line.replace('\n', '').strip()
        if line.strip():
            exist_keywords.append(line)

print(f"type of file:{type(file)}, len of file:{len(exist_keywords)}, head 10:{exist_keywords[:10]}")

# remove exist words
remain_words = set(state_department_keywords) - set(exist_keywords)
print(f"len of remain words:{len(remain_words)}")
remain_sd_keywords_path.write_text('\n'.join(remain_words), encoding='utf-8')

