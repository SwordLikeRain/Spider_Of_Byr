# 思路：当前目标为，自动处理输入的网址，利用selenium爬取数据、进行格式化处理后存储为需要的格式，处理完成后发送邮件给订阅的客户
# 需要处理的，规划一个爬虫时间，其他分类的爬取规则，异常情况处理（超过两天？）
import os
import time
from datetime import datetime
import sys
import re
from selenium import webdriver
from selenium.webdriver.common.by import By


# 从文件中逐行获取网址并分类
def ReadFile():
    f = open("{}".format(sys.argv[1]), "r", encoding="utf-8") # 打开文件名由命令行参数决定

    for line in f.readlines():
        url = re.findall(r'https.* ', line)
        if len(url) != 0:
            if url[0].find('Whisper') != -1:
                Whisper.append(url[0].strip())
            # elif url[0].find('JobInfo') != -1: # 暂停使用JobInfo，需要更新
                # JobInfo.append(url[0].strip())
            else:
                Others.append(url[0].strip())

    f.close()
    with open('{}_TmpSave.txt'.format(datetime.now().strftime("%Y%m%d")), 'w', encoding='utf-8') as f:
        # f.write('JobInfo')
        f.write('Others\n')
        for url in Others:
            f.write(url+' \n')
        f.write("---------------------------------------------------------------------------------------------------------------------------------------------------\n")
        f.write('Whisper\n')
        for url in Whisper:
            f.write(url+' \n')
    return

# 处理悄悄话
def ExcuteWhisper():
    if len(Whisper) != 0:
        file = open('{}_Whisper.txt'.format(datetime.now().strftime("%Y%m%d")), 'a', encoding='utf-8') # 结果存于"日期_Whisper.txt"中，追加写入
        newer_file = open('{}_Whisper_Wait_Updating.txt'.format(datetime.now().strftime(
            "%Y%m%d")), 'a', encoding='utf-8')  # 如果悄悄话近期内还有人回复，将链接存于"日期_Whisper.txt"中，追加写入

        for url in Whisper: # 逐个帖子分析
            file.write(url+'\n') # 写入链接
            page_num = 1 # 帖子总页数
            now_page = 1 # 当前分析的帖子的页号
            comment_seq = 1 # 当前分析的评论的序号
            Stime = '' # 发帖时间
            Ctime = '' # 结帖时间

            browser.get(url) # 打开网页

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
                    # 帖子内容由Fliter()函数处理后写入
                    Qtext,NoMean = Fliter(subtitle.text) # NoMean用于占位
                    if len(Qtext) != 0:
                        file.write("Q："+Qtext)

                # comment_limit本页评论数量，第一页特殊处理（因为第一页最多9个评论、其他页最多10个）
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
                Sendtime = datetime.strptime(Stime+" 12:00", "%Y-%m-%d %H:%M")  # 发帖时间
            Endtime = Sendtime  # 否则以发帖时间为结帖时间
            if Ctime != '':
                Endtime = datetime.strptime(Ctime, "%Y-%m-%d %H:%M")
            
            if (Sendtime.hour >= 22 or Sendtime.hour <= 8): # 深夜贴
                if ((Nowtime - Endtime).total_seconds() / 3600) <= 11:
                    newer_file.write(url+' '+'\n')
            else:
                if ((Nowtime - Endtime).total_seconds() / 3600) <= 6:
                    newer_file.write(url+' '+'\n')
                
            file.write(
                "---------------------------------------------------------------------------------------------------------------------------------------------------\n")
        file.close()
        newer_file.close()
    return

# 对评论内容和帖子内容处理，修改成所需样式，且过滤无意义评论/内容
def Fliter(raw_str):
    strs = raw_str.split('\n') # raw_str是一个由'\n'划分的字符串，用split()分割后处理评论的每一行
    count = 0  # 记录未被过滤的评论行数
    result_str = "" # 返回处理好后的字符串
    rate = "" # 保存赞踩比
    last_comment_time = "" # 最后一条评论的评论时间
    is_rated = False # 是否已经在result_str中保存了赞踩比rate的信息
    is_reply = False # 该字符串是否为帖子的评论（而不是帖子内容）
    for str in strs:
        str = re.sub('^--', '', str) # 过滤--
        str = re.sub('^t', '', str, flags=re.I)  # 过滤t，re.I不区分大小写
        str = re.sub('^rt', '', str, flags=re.I)  # 过滤rt，re.I不区分大小写
        str = re.sub('^[b|z|d]d', '', str, flags=re.I) # 过滤bd、zd、dd
        str = re.sub('\\[bbsemoji[0-9,]+\\]', '', str)  # 过滤无法识别的emoji、中括号的匹配需要在中括号前面加双斜杠\\

        if re.match('^[0-9]+[ ]+[0-9]+$', str) is not None:  # 判断成功，则本行信息为赞踩比，格式化后以字符串形式存在rate中
            agree_num = str.split(' ')[0] # 赞数
            disagree_num = str.split(' ')[1] # 踩数
            if int(agree_num) != 0 or int(disagree_num) != 0:
                rate = rate+"（" + agree_num
            if int(disagree_num) != 0:
                rate = rate+"：" + disagree_num
            if int(agree_num) != 0 or int(disagree_num) != 0:
                rate = rate+'）'

        elif len(str.strip()) != 0:  # 评论有效（未被过滤）
            if re.match('【 在', str) is not None:  # 如果发现这个评论引用了其他评论则判断成功，提前录入赞踩比信息，以满足阅读要求。例如：【 在 IWhisper#992 的大作中提到: 】
                result_str = result_str[:-1]+rate+'\n'
                is_rated = True
            result_str = result_str+str
            result_str = result_str+'\n'
            count = count + 1
            if re.match('沙发|板凳|[0-9]+楼', str) is not None: # 判断该字符串是否为评论，是则判断成功
                result_str = result_str+"A："
                is_reply = True
                data_search = re.search(
                    '([0-9]{4}-[0-9]{2}-[0-9]{2}|今天)[ ]+[0-9]{2}:[0-9]{2}', str)  # 匹配时间字段，将该评论发布时间以last_comment_time返回
                if data_search is not None:
                    last_comment_time = data_search.group()
                    last_comment_time = last_comment_time.replace('今天', datetime.now().strftime("%Y-%m-%d")) # 替换'今天'为日期

    if is_rated != True: # 录入赞踩比信息
        result_str = result_str[:-1]+rate+'\n'
    if count == 2 and is_reply == True: # 过滤无效评论
        result_str = []
    elif result_str == '\n': # 过滤无效评论
        result_str = []
    return result_str,last_comment_time

# 处理工作招聘告示
def ExcuteJobInfo():
    if len(JobInfo) != 0:
        file = open('{}_JobInfo.txt'.format(
            datetime.now().strftime("%Y%m%d")), 'a', encoding='utf-8')  # 结果存于"日期_JobInfo.txt"中，追加写入

        for url in JobInfo:
            file.write(url+'\n') # 写入网址
            browser.get(url)
            time.sleep(1)
            # print(browser.page_source) # browser.page_source直接获取网页源码

            # 获取标题和内容，直接写入
            title = browser.find_elements(By.XPATH, "/html/head/title")
            subtitle = browser.find_element(
                By.CSS_SELECTOR, "#app > div > div > section.thread > div > div.article > div.article-body.content")
            file.write(title[0].text)
            file.write("\n")
            file.write(subtitle.text)
            file.write("\n")
            file.write("------------------------------------------")
        file.close()
    return


def ExcuteOthrs():
    if len(Others) != 0:
        file = open('{}_Others.txt'.format(datetime.now().strftime("%Y%m%d")), 'a', encoding='utf-8')
        for url in Others:
            file.write(url+' '+"\n")
        file.close()
    return



if __name__ == "__main__":
    # 模拟一个手机界面，以绕开登录限制
    WIDTH = 320
    HEIGHT = 640
    PIXEL_RATIO = 3.0
    UA = 'Mozilla/5.0 (Linux; Android 4.1.1; GT-N7100 Build/JRO03C) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/35.0.1916.138 Mobile Safari/537.36 T7/6.3'
    mobileEmulation = {"deviceMetrics": {"width": WIDTH,
                                         "height": HEIGHT, "pixelRatio": PIXEL_RATIO}, "userAgent": UA}
    options = webdriver.ChromeOptions()
    options.add_experimental_option('mobileEmulation', mobileEmulation)

    # 打开浏览器
    browser = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=options)

    # 处理三类信息，悄悄话、招聘、其他
    Others = []
    Whisper = []
    JobInfo=[]
    ReadFile()

    ExcuteJobInfo()
    ExcuteOthrs()
    ExcuteWhisper()

    # 关闭浏览器
    browser.quit()
    os.remove('{}_TmpSave.txt'.format(datetime.now().strftime("%Y%m%d"))) # 正常退出，删除临时文件
