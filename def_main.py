import base64
import json
from tokenize import String
import re
import pandas as pd
from PIL import Image
import os
import shutil
from tkinter import filedialog, messagebox

def image_Path():
    global total_num,filePath,imagePath,imagePath_move,filelist
    imagePath = filedialog.askdirectory()  # 选择图片路径
    filePath = filedialog.askopenfilename()  # 选择csv文件
    imagePath_move = filedialog.askdirectory()  # 已完成图片的保存路径
    filelist = os.listdir(imagePath)  # 打开对应文件夹
    total_num = len(filelist)  # 获取文件内容数量

def csv():
    global lst2,total_num_list,list_T
    # 读取csv文件
    data = pd.read_csv(filePath, header=None)
    # 必须添加header=None，否则默认把第一行数据处理成列名导致缺失
    list_T = data.values.tolist()  # 遍历csv内容数组
    total_num_list = len(list_T)  # csv行数
    lst2 = [item[0] for item in list_T]  # 获取所以数组的第0个

def img_name():
    global imagePath_name,image_hz,count
    imagePath_name = imagePath + '\\' + jpg_name  # 图片路径
    image_hz = str(os.path.splitext(jpg_name)[-1])  # 图片后缀
    image_qz = 'IMAGES/' + jpg_name  # 添加前缀
    count = lst2.count(image_qz)  # 查找该图片在csv中出现的次数
    print(image_qz)
    print(count)

def base_64_Data():
    global base64_data_str
    # 转baes64
    with open(imagePath_name, "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
        base64_data_str = str(base64_data).strip("b''")
        # base64.b64decode(base64data)

def img_size():
    global imgSize,w,h
    # 获取图片尺寸
    img = Image.open(imagePath_name)
    imgSize = img.size
    w = img.width
    h = img.height
    img.close()

def if_image():
    global label_name_str
    if image_hz == '.jpg':
        # label_jpg = re.findall(r'(.+?)\.jpg', jpg_name)  # 去掉后缀
        label_jpg = jpg_name[:-4]
        label_name = label_jpg
    else:
        if image_hz == '.jpeg':
            # label_jpeg = re.findall(r'(.+?)\.jpeg', jpg_name)
            label_jpeg = jpg_name[:-5]
            label_name = label_jpeg
        else:
            if image_hz == '.png':
                # label_png = re.findall(r'(.+?)\.png', jpg_name)
                label_png = jpg_name[:-4]
                label_name = label_png
    label_name_str = str(label_name)

def list_name_H():
    global img_name
    list_H = list_name[0]  # 第l行图片目录
    img_name = (str(list_H).strip('IMAGES/'))

def shapes_dict_date():

    shapes_dict = (
        {
            "label": list_name[5],
            "points": [
                [
                    list_name[1],
                    list_name[2]
                ],
                [
                    list_name[3],
                    list_name[4]
                ]
            ],
            "group_id": None,
            "shape_type": "rectangle",
            "flags": {}
        }
    )
    shapes.append(shapes_dict)

def jdict_():
    global jdict
    jdict = (
        {
            "version": "4.5.7",
            "falgs": {},
            "shapes": shapes,
            "imagePath": jpg_name,
            "imageData": base64_data_str,
            "imageHeight": h,
            "imageWidth": w
        }
    )

def json_out():
    # 输出json
    json_str = json.dumps(jdict, indent=2)
    with open(label_name_str.strip("['']") + '.json', 'w') as json_file:
        json_file.write(json_str)

def shutil_move():
    shutil.move(imagePath_name, imagePath_move)  # 移动已完成图片


image_Path()
csv()
for i in range(total_num):
    jpg_name = filelist[i]  # 图片名
    img_name()
    base_64_Data()
    img_size()
    if_image()

    for l in range(total_num_list):
        list_name = list_T[l]  # 第l行
        list_name_H()
        
        if img_name == jpg_name:
            shapes = []
            for m in range(count):
                list_name = list_T[l]
                shapes_dict_date()
                l = l - 1
            jdict_()
            json_out()

    shutil_move()

print('success!')

messagebox.showinfo('提示', '转换完成')
