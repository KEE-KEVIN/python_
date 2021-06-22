# -*- coding: utf-8 -*-
"""
Created on 2020/11/13 10:31

@author: cosmo
找到最相似的句子
"""
import os
import numpy as np
import joblib

from progressbar import progressbar as pbar
from bert_serving.client import BertClient
import cupy as cp
from bert_vector_convert import VectorConverter
from basic_text_preprocess import Preprocessor
from progressbar import progressbar as pbar


class SimilarFinder(VectorConverter):
    """寻找相似句子"""

    def __init__(self, host, data_path, recommend_num=20, sentence_len_range=None, use_gpu=False):
        super().__init__(host, workers=16, create_conn=True)  # 需要用到父类的一些属性
        self.data_path = data_path
        self.corpus, self.vecs = self.load_sens_vecs(self.data_path)
        self.use_gpu = use_gpu if use_gpu and cp.cuda.runtime.getDeviceCount() > 0 else False
        self.recommend_num = recommend_num
        self.sentence_len_range = sentence_len_range
        if self.use_gpu:
            self.vecs = self.transfer2tensor(self.vecs)

    @staticmethod
    def transfer2tensor(array):
        return cp.asarray(array)

    def similarity_sentences(self, sen):
        vec = self.get_vec(sen)
        candidates = self.square_distance_recommend(vec)
        # print(f"candidates:{candidates}")
        if not self.sentence_len_range:
            candi_sens = [self.corpus[_] for _ in candidates][:self.recommend_num]
        else:
            assert isinstance(self.sentence_len_range, tuple) and len(self.sentence_len_range) == 2 and \
                   self.sentence_len_range[0] <= self.sentence_len_range[1], 'sentence_len_range incorrect!'
            candi_sens = [self.corpus[_] for _ in candidates if
                          self.sentence_len_range[0] <= len(self.corpus[_].strip()) <= self.sentence_len_range[1]
                          ][:self.recommend_num]
        return candi_sens

    def square_distance_recommend(self, vec):
        if not self.use_gpu:  # cpu模式
            distances = np.sqrt(np.sum(np.square(self.vecs - vec), axis=-1)).squeeze()
        else:  # gpu模式
            vec = self.transfer2tensor(vec)
            distances = cp.sqrt(cp.sum(cp.square(self.vecs - vec), axis=-1)).squeeze().get()
            # distances = torch.sqrt(torch.sum(torch.square(self.vecs - vec), dim=-1)).squeeze().numpy()
        return np.argsort(distances).tolist()

    @staticmethod
    def sen_counter(sentences):
        # 句子计数器
        ct = {}
        for sen in sentences:
            ct[sen] = ct.get(sen, 0) + 1
        return ct


if __name__ == '__main__':
    host = '172.16.215.56'
    # data_path = r"E:\AI_data\jinyan_python\data\dataset\noadv.data.pkl"
    # data_path = r"E:\AI_data\jinyan_python\data\dataset\adv_less_strict.pkl"
    data_path = r"E:\AI_data\jinyan_python\data\log_data_specify_purpose\add_group_related.pkl"

    finder = SimilarFinder(host=host, data_path=data_path, recommend_num=3, sentence_len_range=(6, 100), use_gpu=True)
    preprocessor = Preprocessor()
    # sample = '兄弟能加个微信或者QQ吗 可以的话 以后仰仗老哥'
    # sample = '兄弟能加个wx或者QQ吗 可以的话 以后仰仗老哥'
    # sample = '卖，号，有意私聊（40多级）此号5元就能给，买号35级以上50元(永久'
    # sample2 = '300卖本号 要的加好友'
    # sample2 = '卖号了，加我微信的私聊 买号啦，加我微信的私聊 卖升级中20本号，包月卡还剩十多天、还有13000钻石，六十缘，还送18本号一个 300卖本号 要的加好友'
    # sample_poll = ['卖，号，有意私聊（40多级）此号5元就能给，买号35级以上50元(永久', '300卖本号 要的加好友', '卖号了，加我微信的私聊 买号啦，加我微信的私聊',
    #                '出售本号，看上的密。非诚勿扰', '收狮国25左右的号有的联系', '收号！卖的➕85251595', '收资源号，17或18本，出的私聊',
    #                '要资源的加微信JM8484884', '收虎国207级兵号QQ登录出的密', '出号，20级带高迁，要的联系，便宜甩']
    # pool_path = r"E:\AI_data\jinyan_python\data\dataset\ad_dataset_subclass\sell_game_resource.txt"
    pool_path = r"E:\AI_data\jinyan_python\data\dataset\ad_dataset_subclass\add_group.txt"
    sample_poll = preprocessor.load_text(pool_path)
    # sample_poll = ["M15022315828快手看我直播去",
    #                "中国科普网记者为您带来AR智能眼镜现场直播api.topvision-cv.com:8081/topvision/#/meet",
    #                "斗鱼8141503下棋下饭主播求点关注哈哈哈哈",
    #                "现在就是你们来斗鱼6908420点个关注办个卡",
    #                "虎牙17479602关注一波",
    #                "抖音号885350868",
    #                "国王3   小主播，重在参与   q1552533396"]

    all_cands = []
    for sample in pbar(sample_poll):
        cands = finder.similarity_sentences(sample)
        all_cands.extend(cands)
    # cands2 = finder.similarity_sentences(sample2)
    # print('\n'.join(cands))
    all_cands = [_.strip() for _ in all_cands]  # 去除首尾空格
    sentences_counter = finder.sen_counter(all_cands)
    interset = [k for k, v in sentences_counter.items() if v >= 6]  # 出现数超过N的视为可靠样本
    interset = preprocessor._diff_set(interset, sample_poll)  # 除去已有
    interset = preprocessor._deduplication(interset)  # 去重
    print('INTER=>')
    print('\n'.join(interset))
    print(f'totally have {len(interset)} sentence(s).')
    dst_path = input('type output path to save or No to exit:\n')
    if dst_path.lower() not in ['no', 'quit', 'q', 'n']:
        if not os.path.exists(os.path.dirname(dst_path)):
            print('folder does not exist!exit!')
        else:
            mode = 'a' if os.path.exists(dst_path) else 'w'
            with open(dst_path, mode, encoding='utf-8') as f:
                bedump = [_ + '\n' for _ in interset]
                f.write(''.join(bedump))
    else:
        print('exit!')
