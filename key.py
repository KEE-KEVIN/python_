import os
from tkinter import filedialog

# -*- coding: utf-8 -*-
filefile = filedialog.askopenfilename() #选择需要筛选的txt
outfile = open('test.txt','w',encoding='utf-8') #输出的目标txt

with open(filefile,'r',encoding='utf-8') as f:
    for line in f:
        key = line.split('	')[0]
        value = line.split('	')[1]
        count = 0
        for index, line in enumerate(f):
            if key == '1':
                text = value
                outfile.write(text)
                print(value)
                break
            else:
                break
            count += 1

outfile.close()



