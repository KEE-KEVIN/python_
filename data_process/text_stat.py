# -*- coding: utf-8 -*-
"""
Created on 2021/1/13 16:34
@author: cosmo
project name: jinyan_python
file name: text_stat.py
"""
import os

from progressbar import progressbar as pbar


class TextCounter:
    def __init__(self, encoding='utf-8', load_sep='\n', suffix='.txt'):
        self.encoding = encoding
        self.load_sep = load_sep
        self.suffix = suffix

    def load_text(self, src):
        with open(src, 'r', encoding=self.encoding) as f:
            content = f.read().split(self.load_sep)
        content = [_.strip() for _ in content if _.strip()]
        return content

    def load_path_of_files(self, src_dir):
        files = [_ for _ in os.listdir(src_dir) if _.endswith(self.suffix)]
        paths = [os.path.join(src_dir, _) for _ in files]
        return paths

    def lines_count(self, dir_path: str):
        paths = self.load_path_of_files(dir_path)
        info_dt = {}
        for path in pbar(paths):
            content = self.load_text(path)
            name = os.path.basename(path)
            info_dt[name] = len(content)
        return info_dt

    @staticmethod
    def result_print(result_dt, sort=False):
        if sort:
            sort_func = lambda x: x[1]
            result_tuples = sorted(result_dt.items(), key=sort_func)
        else:
            sort_func = lambda x: x[0]
            result_tuples = sorted(result_dt.items(), key=sort_func)
        tplt = "No{0:{3}<4} {1:{3}<35} {2:<10}"
        for _, (k, v) in enumerate(result_tuples):
            print(tplt.format(_, k, v, ' '))  # 中文空格请用chr(12288)


if __name__ == '__main__':
    stat_dir = r"E:\AI_data\jinyan_python\data\dataset\ad_dataset_subclass"
    # stat_dir = r"E:\AI_data\jinyan_python\data\dataset\porn_text_data\test_porn_slices"

    text_counter = TextCounter(encoding='utf-8', load_sep='\n', suffix='.txt')
    text_counter.result_print(text_counter.lines_count(stat_dir), sort=True)
