import os
import re
from tkinter import filedialog

# -*- coding: utf-8 -*-
# filefile = filedialog.askopenfilename() #选择需要筛选的txt
#[微扣🐧邮箱信息消息群联系WwVvQq]+
#^[^\u4e00-\u9fa5]*$ 获取所有非汉字

lineList = []       #创建一个空字典
matchPattern = re.compile(r'^[a-zA-Z0-9]')  #设置关键字
file = open('1_.txt', 'r', encoding='UTF-8')  #打开文本
while 1:
    line = file.readline()
    if not line:
        print("Read file End or Error")
        break
    elif matchPattern.search(line):     #在文本文件中搜索关键词
        lineList.append(line)           #包含关键词的句子添加进字典
    # else:
    #     lineList.append(line)
file.close()
file = open(r'2_.txt', 'w', encoding='UTF-8')  #输入文本
for i in lineList:
    file.write(i)
file.close()


