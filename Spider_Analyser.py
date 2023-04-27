# 目标：
#   自动处理输入的网址，利用selenium爬取数据、进行格式化处理后存储为需要的格式

# version：1.0->1.1
# Author：SwordLikeRain
# Date：2022.11.21->2023.04.27

# 说明：
#   输入：
#       命令行执行时，输入保存待分析网页数据的文件名作为第一个参数，输入文件后缀名应该为.txt
#
#   程序执行：
#       1.从输入文件按行提取出网址并分类为 Whisper和Others，保存分类结果为临时文件"日期_TmpSave.txt"
#       2.将 Others的链接保存为"日期_Others.txt"中
#       3.利用selenium，抓取 Whisper中每个帖子的所需信息，处理后存储在"日期_Whisper.txt"中
#         如果帖子近期内还有人回复，将链接存于"日期_Whisper_Updating.txt"中
#       4.一切运行结束后，删除临时文件"日期_TmpSave.txt"
#       5.移动保存处理好的文件到'db日期'目录，生成下一次的'data.txt'文件（一般由"日期_Whisper_Updating.txt"而来）
#
#   输出：
#       1.正常运行：
#         输出两个文件"日期_Others.txt"和"日期_Whisper.txt"，与原始的输入文件（通常是'data.txt'）共同保存在'db日期'目录下
#         如果 Whisper中有近期回复的帖子，这些帖子的链接会保存在当前文件夹下新产生的'data.txt'中，以便下一次运行时继续处理
#         如果没有，会生成一个新的空的'data.txt'文件，以方便下一次操作
#       2.运行错误中途退出：除去上述文件，额外存在文件"日期_TmpSave.txt"，所有文件都不会被移动到'db日期'目录下
#       3.其他：如果帖子已经被删帖而无法访问网页，会生成"error.txt"文件，并保存在'db日期'目录下
#   注意：
#       一天内多次使用本程序，并不会导致之前的结果被删除，而是追加补充，都存于"日期_Whisper.txt"，逻辑见CreateAndMove()函数
#       不要让程序运行时跨过新的一天，会出现不想管的Bug
#

import os
import time
from datetime import datetime
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.by import By


# 从文件中逐行获取网址并分类，生成用于处理错误的"日期_TmpSave.txt"文件
def ReadFile():
    # 1.从命令行参数的文件中获取url，分类分别保存在 Whisper和 Others中
    # with open('data1.txt', "r", encoding="utf-8") as f:
    with open("{}".format(sys.argv[1]), "r", encoding="utf-8") as f:
        for line in f.readlines():
            url = re.findall(r'https.* ', line)
            if len(url) != 0:
                if url[0].find('Whisper') != -1:
                    # Whisper.append(url[0].strip())
                    Whisper.append(line.strip())
                else:
                    # Others.append(url[0].strip())
                    Others.append(line.strip())

    # 2.保存分类结果为临时文件"日期_TmpSave.txt"，如果产生中断，便于修复
    with open('{}_TmpSave.txt'.format(datetime.now().strftime("%Y%m%d")), 'w', encoding='utf-8') as f:
        f.write('Others\n')
        for url in Others:
            f.write(url.strip()+' \n')
        f.write("---------------------------------------------------------------------------------------------------------------------------------------------------\n")
        f.write('Whisper\n')
        for url in Whisper:
            f.write(url.strip()+' \n')
    return

# 处理悄悄话（Whisper）的 url，抓取每个帖子的所需信息，结果存储在"日期_Whisper.txt"中
# 如果帖子近期内还有人回复，将链接存于"日期_Whisper_Updating.txt"中
def ExcuteWhisper():
    if len(Whisper) != 0:
        # 结果存于"日期_Whisper.txt"中，追加写入
        file = open('{}_Whisper.txt'.format(datetime.now().strftime("%Y%m%d")), 'a', encoding='utf-8') 

        # 如果悄悄话近期内还有人回复，将链接存于"日期_Whisper_Updating.txt"中，追加写入
        newer_file = open('{}_Whisper_Wait_Updating.txt'.format(datetime.now().strftime(
            "%Y%m%d")), 'a', encoding='utf-8')  

        for url in Whisper: # 逐个帖子分析
            
            page_num = 1 # 帖子总页数
            now_page = 1 # 当前分析的帖子的页号
            comment_seq = 1 # 当前分析的评论的序号
            Stime = '' # 发帖时间
            Ctime = '' # 结帖时间

            address = (re.findall(r'https.* ', url))[0].strip()
            browser.get(address) # 打开网页
            try:
                while now_page <= page_num:
                    time.sleep(1) # 等待网页加载

                    # 第一页特殊处理，得到发帖人名称name、发帖时间send_time、帖的赞数title_agree、踩数title_disagree
                    # 帖子总页数page_num、帖子标题title、正文subtitle
                    if now_page == 1:
                        name = browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.article > div.poster.media > div.media-content > div > h4")
                        send_time = browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.thread-header > div > div.column.is-7 > small")
                        Stime = send_time.text
                        title_agree = browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.article > div.poster.media > div.media-right > span:nth-child(3)")
                        title_disagree = browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.article > div.poster.media > div.media-right > span:nth-child(4)")
                        page_num = int(str(browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.paginate > div:nth-child(3) > header > div:nth-child(3) > a").text)[2:].strip())
                        title = browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.thread-header > h2")
                        subtitle = browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.article > div.article-body.content")
                        
                        file.write(url.strip()+' \n')  # 写入链接
                        file.write(send_time.text)
                        file.write("\n")
                        file.write(name.text)
                        file.write("\n")
                        file.write("T："+title.text)

                        # 赞踩比处理后再写入
                        if title_agree.text != 0 or title_disagree.text != 0:
                            file.write("（"+title_agree.text)
                        if title_disagree.text != 0:
                            file.write("："+title_disagree.text)
                        if title_agree.text != 0 or title_disagree.text != 0:
                            file.write("）")
                        file.write("\n")

                        # 发帖内容由Fliter()函数处理后写入
                        Qtext,NoMean = Fliter(subtitle.text) # NoMean用于占位
                        if len(Qtext) != 0:
                            file.write("Q："+Qtext)

                    # comment_limit为本页评论数量，第一页特殊处理（因为第一页最多9个评论、其他页最多10个）
                    comment_limit = len(browser.find_element(
                        By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.posts").find_elements_by_class_name("post"))
                    if now_page == 1:
                        comment_limit = comment_limit+1

                    # 获取评论内容comment并由Fliter()处理后写入
                    while(comment_seq >= (now_page-1)*10 and comment_seq < now_page*10 and comment_seq < (now_page-1)*10+comment_limit):
                        comment = browser.find_element(By.ID, comment_seq)
                        comment_seq = comment_seq + 1
                        Ctext,Ctime = Fliter(comment.text)
                        if len(Ctext) != 0:
                            file.write("---------------------------\n")
                            file.write(Ctext)

                    # 由于直接在链接中修改url无法实现翻页，定位后使用click()模拟翻页
                    if now_page < page_num:
                        browser.find_element(
                            By.CSS_SELECTOR, "#app > div > div > section.paginate > div:nth-child(3) > header > div:nth-child(4)").click()
                    now_page = now_page+1

                # 判断帖子是否还可能被评论
                Nowtime = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M") # 当前时间
                try:
                    Sendtime = datetime.strptime(Stime, "%Y-%m-%d %H:%M") # 发帖时间，超过两天
                except Exception as e:
                    if '今天' in Stime:
                        Stime = Stime.replace('今天', datetime.now().strftime("%Y-%m-%d"))  # 替换'今天'为日期
                        Sendtime = datetime.strptime(Stime, "%Y-%m-%d %H:%M")  # 发帖时间
                    else:
                        Sendtime = datetime.strptime(Stime+" 12:00", "%Y-%m-%d %H:%M")  # 发帖时间
                Endtime = Sendtime  # 否则以发帖时间为结帖时间
                if Ctime != '':
                    Endtime = datetime.strptime(Ctime, "%Y-%m-%d %H:%M")
                
                if (Sendtime.hour >= 22 or Sendtime.hour <= 8): # 深夜贴
                    if ((Nowtime - Endtime).total_seconds() / 3600) <= 11:
                        newer_file.write(url.strip()+' '+'\n')
                else:
                    if ((Nowtime - Endtime).total_seconds() / 3600) <= 6:
                        newer_file.write(url.strip()+' '+'\n')
                    
                file.write(
                    "---------------------------------------------------------------------------------------------------------------------------------------------------\n")
            except: # 帖子打不开
                with open('error.txt', 'a', encoding='utf-8') as f:
                    f.write(url.strip()+' \n')
        file.close()
        newer_file.close()
    return

# 对评论内容和帖子内容处理，修改成所需样式，且过滤无意义评论/内容
# 输入的 raw_str是一个由'\n'划分的字符串，用split()分割后处理评论的每一行
def Fliter(raw_str):
    strs = raw_str.split('\n') 
    count = 0  # 记录未被过滤的评论行数
    result_str = "" # 返回处理好后的字符串
    rate = "" # 保存赞踩比
    last_comment_time = "" # 最后一条评论的评论时间
    is_rated = False # 是否已经在result_str中保存了赞踩比rate的信息
    is_reply = False # 该字符串是否为帖子的评论（而不是帖子内容）

    for str in strs:

        # 过滤符号
        str = re.sub('\\[bbsemoji[0-9,]+\\]', '', str)  # 过滤无法识别的emoji、中括号的匹配需要在中括号前面加双斜杠\\
        str = re.sub('^--', '', str) # 过滤--
        str = re.sub('^t', '', str, flags=re.I)  # 过滤t，re.I不区分大小写
        str = re.sub('^rt', '', str, flags=re.I)  # 过滤rt，re.I不区分大小写
        str = re.sub('^[b|z|d]d', '', str, flags=re.I) # 过滤bd、zd、dd
        
        # 判断成功，则本行信息为评论的赞踩比，格式化后以字符串形式存在rate中，之后添加在对应位置
        if re.match('^[0-9]+[ ]+[0-9]+$', str) is not None:  
            agree_num = str.split(' ')[0] # 赞数
            disagree_num = str.split(' ')[1] # 踩数
            if int(agree_num) != 0 or int(disagree_num) != 0:
                rate = rate+"（" + agree_num
            if int(disagree_num) != 0:
                rate = rate+"：" + disagree_num
            if int(agree_num) != 0 or int(disagree_num) != 0:
                rate = rate+'）'

        # 评论有效（未被过滤）
        elif len(str.strip()) != 0:

            # 如果发现这个评论引用了其他评论则判断成功，提前录入赞踩比信息，以满足阅读要求。例如：【 在 IWhisper#992 的大作中提到: 】
            if re.match('【 在', str) is not None: 
                result_str = result_str[:-1]+rate+'\n'
                is_rated = True

            result_str = result_str+str
            result_str = result_str+'\n'
            count = count + 1

            # 判断该字符串是否为评论开头，是则判断成功
            if re.match('沙发|板凳|[0-9]+楼', str) is not None: 
                result_str = result_str+"A："
                is_reply = True

                # 匹配时间字段，将该评论发布时间以last_comment_time返回
                data_search = re.search(
                    '([0-9]{4}-[0-9]{2}-[0-9]{2}|今天)[ ]+[0-9]{2}:[0-9]{2}', str)  
                if data_search is not None:
                    last_comment_time = data_search.group()
                    last_comment_time = last_comment_time.replace('今天', datetime.now().strftime("%Y-%m-%d")) # 替换'今天'为日期

    if is_rated != True: # 录入赞踩比信息
        result_str = result_str[:-1]+rate+'\n'
    if count == 2 and is_reply == True: # 过滤无效评论，该评论除了发评论人和发评论时间，其他信息均无效
        result_str = []
    elif result_str == '\n': # 过滤无效评论
        result_str = []
    return result_str,last_comment_time

# 非Whisper即为Others，将 Others的 url保存为"日期_Others.txt"中
def ExcuteOthrs():
    if len(Others) != 0:
        file = open('{}_Others.txt'.format(datetime.now().strftime("%Y%m%d")), 'a', encoding='utf-8')
        for url in Others:
            file.write(url.strip()+' '+"\n")
        file.close()
    return

# 文件善后，移动保存处理好的文件到'db日期'目录，生成下一次的'data.txt'文件
def CreateAndMove():
    # 如果不存在'db日期'目录，创建目录
    dir = "db"+datetime.now().strftime("%Y%m%d")[2:]
    if not os.path.exists(dir):
        os.mkdir(dir)

    # 将文件移动到指定目录
    Whisper_Address = '{}_Whisper.txt'.format(datetime.now().strftime("%Y%m%d"))
    Other_Address = '{}_Others.txt'.format(datetime.now().strftime("%Y%m%d"))
    Temp_Address = '{}_Whisper_Wait_Updating.txt'.format(datetime.now().strftime("%Y%m%d"))

    # 如果'日期_Whisper.txt'存在，输出行数
    # 检测'db日期'目录是否存在'日期_Whisper.txt'，如果文件已经存在，将目前'日期_Whisper.txt'作为原文件的追加，否则直接移动
    if os.path.exists(Whisper_Address):
        # 输出'日期_Whisper.txt'的行数
        with open(Whisper_Address, 'r', encoding='utf-8') as f:
            print('Whisper.txt has {} lines.'.format(len(f.readlines())))

        # 检测'db日期'目录是否存在'日期_Whisper.txt'，如果文件已经存在，将目前'日期_Whisper.txt'作为原文件的追加，否则直接移动
        if os.path.exists(dir+'/'+Whisper_Address):
            with open(dir+'/'+Whisper_Address, 'a', encoding='utf-8') as f:
                with open(Whisper_Address, 'r', encoding='utf-8') as f1:
                    for line in f1.readlines():
                        f.write(line)
            os.remove(Whisper_Address)
        else:
            os.rename(Whisper_Address, dir+'/'+Whisper_Address)

    # 如果'日期_Others.txt'存在，输出行数
    # 将目前'日期_Others.txt'直接移动到'db日期'目录
    if os.path.exists(Other_Address):
        with open(Other_Address, 'r', encoding='utf-8') as f:
            print('Others.txt has {} lines.'.format(len(f.readlines())))
        os.rename(Other_Address, dir+'/'+Other_Address)

    # 'data.txt'数据更新
    if os.path.exists(dir+'/'+'data.txt'):
        os.remove('data.txt')
    else:
        os.rename('data.txt', dir+'/'+'data.txt')

    # 'Temp.txt'如果存在，成为新的'data.txt'
    # 否则，没有更多数据需要获取，创建新的'data.txt'
    if os.path.exists(Temp_Address):
        os.rename(Temp_Address, 'data.txt')
        print('Temp file detected!')
    else:
        with open('data.txt', 'w', encoding='utf-8') as f:
            f.write('')
        print('New data.txt created!')

    # 如果'error.txt'存在，输出行数
    # 检测'db日期'目录是否存在'error.txt'，如果文件已经存在，将目前'error.txt'作为原文件的追加，否则直接移动
    if os.path.exists('error.txt'):
        with open('error.txt', 'r', encoding='utf-8') as f:
            print('error.txt detected with {} lines.'.format(len(f.readlines())))

        if os.path.exists(dir+'/'+'error.txt'):
            with open(dir+'/'+'error.txt', 'a', encoding='utf-8') as f:
                with open('error.txt', 'r', encoding='utf-8') as f1:
                    for line in f1.readlines():
                        f.write(line)
            os.remove('error.txt')
        else:
            os.rename('error.txt', dir+'/'+'error.txt')


if __name__ == "__main__":
    # 模拟一个手机界面，以绕开登录限制
    WIDTH = 320
    HEIGHT = 640
    PIXEL_RATIO = 3.0
    UA = 'Mozilla/5.0 (Linux; Android 4.1.1; GT-N7100 Build/JRO03C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3'
    mobileEmulation = {"deviceMetrics": {"width": WIDTH,
                                         "height": HEIGHT, "pixelRatio": PIXEL_RATIO}, "userAgent": UA}
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # 无头模式，关闭浏览器显示
    options.add_experimental_option('mobileEmulation', mobileEmulation)

    # 打开浏览器
    browser = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)

    # 处理两类信息，悄悄话、其他
    Others = []
    Whisper = []
    ReadFile()

    ExcuteOthrs()
    ExcuteWhisper()

    # 关闭浏览器
    browser.quit()

    # 正常退出，删除临时文件
    if os.path.exists('{}_TmpSave.txt'.format(datetime.now().strftime("%Y%m%d"))):
        os.remove('{}_TmpSave.txt'.format(datetime.now().strftime("%Y%m%d"))) 
    with open('{}_Whisper_Wait_Updating.txt'.format(datetime.now().strftime("%Y%m%d")), 'r', encoding='utf-8') as f:
        length=len(f.read())
    if length == 0:
        os.remove('{}_Whisper_Wait_Updating.txt'.format(datetime.now().strftime("%Y%m%d")))

    # 善后处理
    CreateAndMove()