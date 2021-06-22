# -*- coding: utf-8 -*-
# @Time    : 2021/3/10 16:16
# @Author  : cosmo
# @Project : jinyan_python
# @File    : sensitive_words_process.py

from pathlib import Path


src_path = Path(r"E:\AI_data\jinyan_python\doc\敏感词资源\屏蔽词库-2020国务院.txt")
dst_path = Path(r"state_department_keywords_2020.txt")

content = src_path.read_text(encoding='utf-8')
words_lines = content.split('\n')
words = []
for line in words_lines:
    words.extend(line.split('、'))
# remove blank
words = [_.strip() for _ in words if _.strip()]
print(f"totally have {len(words)} word(s)")

# write into plain text
dst_path.write_text(data='\n'.join(words), encoding='utf-8')

