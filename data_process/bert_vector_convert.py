# -*- coding: utf-8 -*-
"""
Created on 2020/11/13 10:37

@author: cosmo
"""


import os
import numpy as np
import joblib

from progressbar import progressbar as pbar
from bert_serving.client import BertClient


class VectorConverter:
    """将短文本转换为定长的bert向量"""
    def __init__(self, host, workers=16, create_conn=True):
        self.host = host
        self.workers = workers  # 获取向量的batch数量
        self.create_conn = create_conn
        if self.create_conn:
            self.bc = self.create_client()
            print('client ok.')

    @staticmethod
    def load_text(path):
        with open(path, 'r', encoding='utf-8') as f:
            sens = f.read().split('\n')
        new_sens = list(set(sens))
        # for _ in sens:  # 去重且尽量保持顺序
        #     if _ not in set(new_sens):
        #         new_sens.append(_.strip())
        return new_sens

    def create_client(self):
        return BertClient(ip=self.host)

    def get_vec(self, sen):
        # 获取单个文本的编码向量
        bc = self.bc if self.create_conn else self.create_client()
        vec = bc.encode([sen])[0]
        if not self.create_conn:
            bc.close()
        return vec

    def collect_vecs(self, sens):
        # 收集歌句库的向量
        bc = self.bc if self.create_conn else self.create_client()
        vec_pieces = []
        sentence = []
        for head in pbar(range(len(sens) // self.workers + 1)):
            span = sens[head * self.workers:(head + 1) * self.workers]
            vecs = bc.encode(span)
            vec_pieces.append(vecs)
            sentence.extend(span)
        all_vecs = np.concatenate(vec_pieces, axis=0)
        if not self.create_conn:
            bc.close()
        return tuple(sentence), all_vecs

    @staticmethod
    def save_sens_vecs(sens, vecs, dst):
        joblib.dump((sens, vecs),dst)

    @staticmethod
    def load_sens_vecs(src):
        return joblib.load(src)





if __name__ == '__main__':
    host = '172.16.215.56'  # 2x E5 2x 2070
    # src = r"E:\AI_data\jinyan_python\data\dataset\noadv.data.txt"
    # src = r"E:\AI_data\jinyan_python\data\dataset\adv.data.txt"
    # src = r"E:\AI_data\jinyan_python\data\dataset\adv_less_strict.txt"
    src = r"E:\AI_data\jinyan_python\data\log_data_specify_purpose\add_group_related.txt"
    dst = src.replace('.txt', '.pkl')

    converter = VectorConverter(host=host, workers=64, create_conn=True)
    corpus = converter.load_text(src)
    print('文本读取成功。')
    sens, vecs = converter.collect_vecs(corpus)
    converter.save_sens_vecs(sens, vecs, dst)
