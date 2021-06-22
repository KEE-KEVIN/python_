# -*- coding: utf-8 -*-
"""
Created on 2020/11/30 16:16

@author: cosmo
"""
'''
Author: your name
Date: 2020-08-11 14:10:25
LastEditTime: 2020-09-14 15:09:45
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /game_ban_chat/data_process/log_data_chat_str_filter.py
'''
import os
import re

from progressbar import progressbar as pbar

# file_path = r"F:\ai_dataset\jinyan_log\downloaded_data_buluozhanhun30days.txt"
# save_path = './buluozhanhun_chat_str.txt'

file_path = r"E:\AI_data\jinyan_python\server_log_data\wrong_pred_data\data_20201126_101248.txt"
save_path = r"E:\AI_data\jinyan_python\server_log_data\wrong_pred_data\wrong_pred_filtered.txt"

with open(file_path,'r', encoding='utf-8') as f:
    content = f.readlines()

sentences = []
# patten = "(?<='chat_str'\: ').*(?=', 'summary_context')" # filter char_str
patten = "(?<='summary_context'\: ').*(?=', 'suggestion')" # filter summary_context

for line in pbar(content):
    # print(f"line:{line}")
    sen = re.findall(patten, line)
    if not sen or len(sen[0]) < 20:  # 跳过不为空的和比较短的
        continue
    else:
        sen = sen[0]
    if sen not in sentences:
        sentences.append(sen)

print(f"totaly have {len(sentences)} sentences")

with open(save_path, 'w', encoding='utf-8') as wf:
    wf.write('\n'.join(sentences))
