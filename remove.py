import re
from tkinter import filedialog

# filefile = filedialog.askopenfilename() #选择需要筛选的txt

lineList = []
matchPattern = re.compile(r'^[a-zA-Z0-9]')
file = open('1_.txt', 'r', encoding='UTF-8')
while 1:
    line = file.readline()
    if not line:
        print("Read file End or Error")
        break
    elif matchPattern.search(line):
        pass
    else:
        lineList.append(line)
file.close()
file = open(r'1_.txt', 'w', encoding='UTF-8')
for i in lineList:
    file.write(i)
file.close()
