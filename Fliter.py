# 目标：
#   自动处理输入的文件，根据输入的参数选择删除文件的重复url还是删除文件的重复过时帖子

# version：1.0
# Author：SwordLikeRain
# Date：2022.11.22

# 说明：
#   输入：
#       命令行执行时，输入待分析的文件名作为第一个参数，输入文件后缀名应该为.txt，第二个参数可以是0，也可以不填
#
#   程序执行：
#       1.从输入文件按行提取内容形成列表，保存在garphs中
#       2.根据第二个参数是否为0，分支执行
#     2.1.如果是0，则调用Excute_Whisper()函数，去除文件的重复过时帖子
#     2.2.否则，调用Fliter_Url()函数，删除文件中的重复url
#       4.一切运行结束后，将去重结果保存在'源文件名_after.txt'中
#
#   输出：
#       1.去重结果保存在'源文件名_after.txt'中

import sys
import re

# 删除graphs中的重复帖子（优先保留排序靠后的版本），返回删除后的帖子构成的列表（按行）
def Excute_Whisper():
    # 同一下标seq下，authors[seq]和questions[seq]分别是graphs[seq]的作者和Q部分
    graphs = []  # 以列表形式保存的帖子
    authors = []  # 以列表形式保存的作者
    questions = []  # 以列表形式保存的Q
    author = ""  # 帖子的作者名称，用于定位帖子
    question = ""  # 帖子的Q部分，用于定位帖子
    graph = ""  # 帖子内容
    state = 0  # 初始状态

    i = 0
    while i < len(lines):
        line = lines[i] # 本行内容
        i += 1
        graph += (line+'\n') # 将本行内容添加到帖子中
        if line[:10] == '----------' and len(line) >= 45: # 下一个帖子的分隔符
            seq = 0
            while seq < len(authors): # 寻找是否已经保存该帖，依据发帖人和发帖问题筛选，都相同则认为为同一帖
                if authors[seq] == author and questions[seq] == question:
                    break
                seq += 1
            if seq != len(authors): # 将过时的该贴删除
                graphs.pop(seq)
                authors.pop(seq)
                questions.pop(seq)
            graphs.append(graph)
            authors.append(author)
            questions.append(question)
            graph = ""
            state = 0

        # 简单状态机，用于获取author和question字段值
        if state == 0 and re.search('^[0-9]{4}-[0-9]{2}-[0-9]{2}', line) is not None: 
            state = 1
        elif state == 1 and line.strip() != '':
            author = line
            state = 2
        elif state == 2 and line .strip() != '':
            question = line[:line.index('（')]
            state = 3
    return graphs


# 删除graphs种的重复url后返回列表
def Fliter_Url():
    graphs = []
    for url in lines:
        if url not in graphs:
            graphs.append(url+'\n')
    return graphs

if __name__ == "__main__":
    with open("{}".format(sys.argv[1]), "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    graphs = []
    if '0' == sys.argv[2]:
        graphs = Excute_Whisper()
    else:
        graphs = Fliter_Url()

    with open("{}".format(sys.argv[1])[:-4]+'_after.txt', "w", encoding="utf-8") as f:
        for graph in graphs:
            f.write(graph)