# -*- coding: utf-8 -*-
"""
Created on 2020/11/17 16:46

@author: cosmo
基本的文本预处理类
"""
import os


class Preprocessor:
    """基本的文本预处理类（以行为基本单位），主要功能如下:
    1.文本去重(去首位空格)
    2.大小写转换(通过控制参数决定是小写化还是大写化)
    3.简繁体转换
    4.全角半角转换
    5.文本差集
    6.文本并集(支持多个文本，并自动对结果去重)"""

    def __init__(self, load_sep='\n', write_sep='\n', encoding='utf-8'):
        self.load_sep = load_sep
        self.write_sep = write_sep
        self.encoding = encoding

    @staticmethod
    def _remove_blank(lines):
        return [_.strip() for _ in lines]

    def load_text(self, src):
        with open(src, 'r', encoding=self.encoding) as f:
            content = f.read().split(self.load_sep)
        content = [_.strip() for _ in content if _.strip()]
        return content

    def dump_text(self, content, dst, mode='w'):
        with open(dst, mode, encoding=self.encoding) as f:
            if isinstance(content, str):
                f.write(content)
            elif isinstance(content, (list, tuple, set)):
                f.write(self.write_sep.join(content))
            else:
                raise TypeError('content should be str or iterable obj!')

    @staticmethod
    def _deduplication(lines):
        new_lines = []
        lines_set = set()
        for line in lines:
            line = line.strip()
            if line not in lines_set:
                new_lines.append(line)
            lines_set.add(line)
        return new_lines

    @staticmethod
    def _diff_set(a: (list, tuple, set), b: (list, tuple, set)):
        """return diff-set of a - b"""
        b = set(b)
        new_a = [_ for _ in a if _ not in b]
        return new_a

    def deduplication(self, src, dst=None, replace=False):
        """指定输入核输出目录，对单个文本进行去重。replace为真是可以使输出替换输入文件"""
        assert bool(dst) ^ replace, 'dst and replace must be XoR relationship!'
        content = self.load_text(src)
        new_content = self._deduplication(content)
        dump_path = src if replace else dst
        self.dump_text(content=new_content, dst=dump_path)
        print(f"output path:[{dump_path}]")
        print(f"removed {len(content)-len(new_content)} item(s).")

    def diff_text(self, a_path: str, b_path, dst=None, replace=False):
        """给予被减文本和减文本的路径，输出被减后的新文本
        在此过程会自动去重，replace可以控制是否替换源文件"""
        assert bool(dst) ^ replace, 'dst and replace must be XoR relationship!'
        a_content, b_content = self.load_text(a_path), self.load_text(b_path)
        new_a_content, new_b_content = self._deduplication(a_content), self._deduplication(b_content)
        new_a_content = self._diff_set(new_a_content, new_b_content)
        dump_path = a_path if replace else dst
        self.dump_text(content=new_a_content, dst=dump_path)
        print(f"output path:[{dump_path}]")
        print(f"removed {len(a_content) - len(new_a_content)} item(s).")

    def _union_load(self, filenames):
        if isinstance(filenames, str):  # 是个目录
            names = os.listdir(filenames)
            filenames = [os.path.join(filenames, _) for _ in names if os.path.isfile(os.path.join(filenames, _))]
        container = []
        for filename in filenames:
            content = self.load_text(filename)
            container.extend(content)
        return container

    def union_text(self, filenames: list, dst: str, union_log=True):
        """将多个文本合并且去重"""
        container = self._union_load(filenames)
        container = self._deduplication(container)
        self.dump_text(container, dst)
        print(f"output path:[{dst}]")
        print(f"totally have {len(container)} item(s).")
        if union_log:
            log_file = dst+'.log'
            self.dump_text(filenames, dst=log_file)
            print(f"union log at:[{log_file}]")

    @staticmethod
    def collect_filenames(src_dir:str)->list:
        files = os.listdir(src_dir)
        filenames = [os.path.join(src_dir, file) for file in files]
        return filenames



if __name__ == '__main__':
    processor = Preprocessor()

    # 去重测试
    # src = r"E:\AI_data\jinyan_python\doc\敏感词资源\state_department_keywords_2020.txt"
    # dst = r"E:\AI_data\jinyan_python\data\dataset\ad_dataset_subclass\test.txt.deduplicate"
    # processor.deduplication(src=src, dst=None, replace=True)

    # 文本相减测试（a-b）
    a_path = r"C:/Users/longyuan/Desktop/暴恐1.txt"
    b_path = r"C:/Users/longyuan/Desktop/暴恐.txt"
    dst = r"C:/Users/longyuan/Desktop/date/1_相减.txt"
    processor.diff_text(a_path, b_path, dst=dst, replace=False)

    # 文本合并测试
    # src_files = [r"F:\temp_files\zzq_keywords\国内词汇\屏蔽词v2_part1.txt",
    #              r"F:\temp_files\zzq_keywords\国内词汇\屏蔽词v2_part2.txt",
    #              r"F:\temp_files\zzq_keywords\国内词汇\屏蔽词v2_part3.txt"]
    # src_files = processor.collect_filenames(r"F:\ai_dataset\敏感词库人审\敏感词二级标签\一级分类")
    # dst = r"F:\ai_dataset\敏感词库人审\敏感词二级标签\所有系统词.txt"
    # processor.union_text(src_files, dst=dst)

