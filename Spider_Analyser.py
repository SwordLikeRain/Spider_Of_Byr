# 思路：当前目标为，自动处理输入的网址，利用selenium爬取数据、进行格式化处理后存储为需要的格式

from selenium import webdriver
browser = webdriver.Chrome()
# browser.minimize_window()  # 最小化窗口
url = 'https://bbs.byr.cn/#!article/IWhisper/4841523?p=1'
browser.get(url)
info=browser.find_elements_by_class_name('info')
#在目标网站中网站中标题class名称都为"info"，所以用elements
for i in info:
    print(i.text)
    #.text为定位元素底下的所有文本，当然我们也可以获取标签里的东西（用其它函数），如视频链接：
    # print(i.find_elements_by_tag_name('a')[0].get_attribute('href'))