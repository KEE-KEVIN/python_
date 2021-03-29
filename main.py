import base64
import json
import pandas as pd
from PIL import Image
import os
import shutil
from tkinter import filedialog,messagebox




imagePath = filedialog.askdirectory()#选择图片路径

imagePath_src = imagePath

filePath = filedialog.askopenfilename()#选择csv文件
imagePath_move = filedialog.askdirectory()#已完成图片的保存路径


filelist = os.listdir(imagePath)  # 打开对应文件夹
total_num = len(filelist)  # 获取文件内容数量

for i in range(total_num):
    jpg_name = filelist[i]  # 图片名
    imagePath_name = imagePath + '\\' + jpg_name  # 图片路径

    image_hz = str(os.path.splitext(jpg_name)[-1])  # 图片后缀

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

    # 转baes64
    with open(imagePath_name, "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
        base64_data_str = str(base64_data).strip("b''")
        # base64.b64decode(base64data)

    # 获取图片尺寸
    img = Image.open(imagePath_name)
    imgSize = img.size
    w = img.width
    h = img.height
    img.close()

    # 读取csv文件
    data = pd.read_csv(filePath, header=None)
    # 必须添加header=None，否则默认把第一行数据处理成列名导致缺失
    list_T = data.values.tolist()
    total_num_list = len(list_T)

    for l in range(total_num_list):
        list_name = list_T[l]
        list_H = list_name[0]
        img_name = (str(list_H).strip('IMAGES/'))
        if img_name == jpg_name:
            points = [list_name[1], list_name[2]], [list_name[3], list_name[4]]
            label = list_name[5]

    
            jdict = (
                {
                "version": "4.5.7",
                "falgs": {},
                "shapes": [
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
                ],
                "imagePath": jpg_name,
                "imageData": base64_data_str,
                "imageHeight": h,
                "imageWidth": w
            }
        )

    json_str = json.dumps(jdict, indent=2)
    with open(label_name_str.strip("['']") + '.json', 'w') as json_file:
        json_file.write(json_str)

    shutil.move(imagePath_name,imagePath_move)



messagebox.showinfo('提示','转换完成')


