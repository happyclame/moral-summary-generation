# coding=utf-8
#导入jieba及自定义词典
import numpy as np
from typing import List, Iterable
import jieba
import jieba.analyse
jieba.load_userdict('道德动机词合并.txt')
import scipy as scipy
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from math import gcd
from typing import List, Iterable

# 函数（一）：输入包含句子的列表，输出为结巴分词后的词列表（采用自定义词典切割）
def get_segment(words):
    new_words = []
    for i in words:
        word = jieba.lcut(i)
        new_words = new_words + word
    return new_words


#调整分段窗口函数
def read(filepath: str, nRows: int) -> Iterable[List[str]]:
    i = 0
    lines = []  # a buffer to cache lines
    with open(filepath,'r',encoding="UTF-8" ) as f:
        for line in f:
            i += 1
            lines.append(line.strip())  # append a line
            if i >= nRows:
                yield lines
                # reset buffer
                i = 0
                lines.clear()
    # remaining lines
    if i > 0:
        yield lines

# 函数（二）：输入的是标注字典中的句子，输出为结巴分词后的词列表（采用自定义词典切割）
def get_sent_segment(sent):
    new_words = []
    word = jieba.lcut(sent)
    new_words = new_words + word
    return new_words


# 函数（三）：输入为两个包含词的列表，返回四个列表
# （1）两个列表的交集（不去重）
# （2）两个列表的交集（去重）
# （3）第一个返回的列表的长度（不去重单词数）
# （4）第二个返回的列表的长度（去重后单词数）
def compare_word(words1, words2):
    union = [word for word in words1 if word in words2]
    union_set = set(union)
    union_num = len(union)
    union_set_num = len(union_set)
    return union, union_set, union_num, union_set_num


# 函数（四）：TextRank抽取关键句
def keysentences_extraction(text):
    tr4s = TextRank4Sentence()
    tr4s.analyze(text, lower=True, source='all_filters')
        # text    -- 文本内容，字符串
        # lower   -- 是否将英文文本转换为小写，默认值为False
        # source  -- 选择使用words_no_filter, words_no_stop_words, words_all_filters中的哪一个来生成句子之间的相似度。
        # 		  -- 默认值为`'all_filters'`，可选值为`'no_filter', 'no_stop_words', 'all_filters'
        # sim_func -- 指定计算句子相似度的函数

        # 获取最重要的num个长度大于等于sentence_min_len的句子用来生成摘要
    keysentences = tr4s.get_key_sentences(num=5, sentence_min_len=3)
    return keysentences


# 调用函数（三）：输入为小说分词后的词列表A和道德能动词表agency，计算交集，最后返回四个列表：
f2 = open(u'agency.txt', 'r', encoding='utf-8')
B = f2.readlines()
B_list = [x.strip() for x in B if x.strip()!='']

# 调用函数（三）：输入为小说分词后的词列表A和道德能动词表communion，计算交集，最后返回四个列表：
f3 = open(u'communion.txt', 'r', encoding='utf-8')
C = f3.readlines()
C_list = [x.strip() for x in C if x.strip()!='']


#正式流程-------------------------------------------

#读取文件 数据预处理:以n为单位切分段落，储存为新文件
datafile = "盗墓笔记by南派三叔.txt"
lines_gen = read(datafile, 10)
f = open("cut.txt", "w", encoding='utf-8')
for lines in lines_gen:
        s = ''.join(lines)
        f.write(s+"\n")
        # print(s)

#读取文件 以列表形式储存
f1 = open('cut.txt', 'r', encoding='utf-8')
text = f1.readlines()
text = [x.strip() for x in text if x.strip()!='']
# print(text)
sent2score = []  #建立空列表，存储段落及其分值

#计算道德动机值
for i in text:
    #求agency和communion词频
    A_list = get_sent_segment(i)
    # print(A_list)
    joint_agency = compare_word(A_list, B_list)
    data_agency = joint_agency[2]
    joint_communion = compare_word(A_list, C_list)
    data_communion = joint_communion[2]

    if data_agency  != 0 :
        if data_communion != 0 :
            data_moral = [i,]
            score_moral = data_communion * 722 / (data_agency * 290)
            data_moral.append(score_moral)

            score_agency = []
            sc_agency = data_agency / 722
            score_agency.append(sc_agency)

            score_communion = []
            sc_communion = data_communion / 290
            score_communion.append(sc_communion)
            sent2score.append(data_moral)
            # print(data_moral)

#排序并筛选道德动机值高的前n个段落
sent2score2 = sorted(sent2score,key=(lambda x:x[1]),reverse=True)
sent2score3 = sent2score2[:50]
print('--------------------------')
print('本小说中道德动机值高的段落为：')
print(sent2score3)

#组成新素材文件
f4 = open("newfile.txt", "w")
for i in sent2score3:
    j = i[0]
    # print(j)
    f4.write(j+"\n")

# textrank抽取摘要
if __name__ == "__main__":
    text = open('newfile.txt').read()


print('--------------------------')
print("小说摘要为：")
keysentences = keysentences_extraction(text)
for i in keysentences:
    j = i.get('sentence')
    print(j,end='。')



f.close()
f1.close()
f2.close()
f3.close()
f4.close()
