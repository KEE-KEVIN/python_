import json
import os
from tkinter import filedialog,simpledialog,messagebox

def selectJsPath():
    global Jspath_
    Jspath_ =filedialog.askopenfilename()

def selectPath():
    global path_
    path_ = filedialog.askdirectory()
def selectvalue():
    global ranget
    t = simpledialog.askstring('Title','请输入需要修改的文件数量',initialvalue='')
    ranget = int(t)

# 获取json中shapes值
def js_sh():
    global sh
    jsonPath = str(Jspath_)
    with open(jsonPath, "r") as f:
        json_str = f.read()
    your_dict = json.loads(json_str)
    sh = your_dict["shapes"]
    print(sh)

def js_path():
    global jsonlist,js_path_line
    # 获取需要修改json文件目录
    js_path_line = str(path_)
    jsonlist = os.listdir(js_path_line)
    line_js = len(jsonlist)

def js_sp():
    for l in range(ranget):
        js_ = jsonlist[l]
        json_qz_path = js_path_line + '/' + js_  # 添加前缀,获取完整路径
        with open(json_qz_path, 'rb') as f:
            params = json.load(f)
        params['shapes'] = sh
    # print("params", params)
        dict = params

# with open(json_qz_path, 'w') as f:
#     json.dumps(dict,f)
        json_str = json.dumps(dict, indent=2)
        with open(json_qz_path, 'w') as json_file:
            json_file.write(json_str)


if __name__ == '__main__':

    selectPath()
    selectJsPath()
    selectvalue()

    js_sh()
    js_path()
    js_sp()
















