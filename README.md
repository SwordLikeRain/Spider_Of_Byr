# 一个基于Python3的利用Selenium实现BYR论坛帖子抓取的爬虫和利用PyQt5实现GUI界面帮助分析数据的资料获取和分析系统
> ---作者：SwordLikeRain  
> ---当前版本：v1.0->v1.1
> ---更新时间：2022.11.22->2023.04.27
## 0开发背景  
- BYR论坛"悄悄话"的海量帖子中[^1]，蕴含着信息的宝藏。我们可以白天把这些帖子的链接保存下来，晚上一个个打开链接比对筛选信息，但这未免有些太过低效，而如果不保存这些帖子，3天后会它们会被自动删除。
- 那么，一个自动抓取我觉得有效的帖子的爬虫，和一个帮助分析过滤帖子内容的图形化界面的需求就应运而生。
- 恰巧最近封校很空闲，为了心理健康和技术追求，我就花了10天时间写了这么一个简单的系统（严格来说暂时也不算系统），它在读取我关注的帖子链接构成的文件后（不只是"悄悄话"），可以将其内容爬取并分类保存 **【不需要登录论坛！！！】**。然后在图形化界面，我可以对其进行进一步筛选并由程序保存成我想要的格式。    
- 我还借此练习了*MarkDown*的语法以及*Vscode在Github*的操作，把之前欠下来没学的知识还还账...  
## 1技术说明
> 1. Selenium。本来是网页自动化测试工具，能够通过代码完全模拟人使用浏览器自动访问目标站点并操作来进行web测试。但用来写一个频率没那么高要求[^2]，且防止被反爬[^3]的爬虫，它已经是绰绰有余。同时在实践中，我发现它有一个大优势，即**可以模拟移动端，使得不需要登录账号就可以获取内容。**
> 2. PyQt5。QT在Python下的图形化工具，学了它顺便为以后毕设做原型系统铺垫。
## 2环境配置
1. **Python3**。安装略，本机环境为 **Python 3.9.9**。
2. **Selenium**：使用```pip3 install selenium```安装相关库，再安装一个浏览器驱动，参考[这个链接](https://blog.csdn.net/sgld995/article/details/123451146)。本机环境为 **Version: 4.2.0**。
3. **PyQt5**：```pip install PyQt5```。本机环境为 **Version: 5.15.4**。
## 3整体介绍  
本系统目前共分为3部分，分别为：
1. ***Spider_Analyser.py*** 和 ***Spier_Others.py***。自动处理输入的包含网址的文件，利用selenium爬取数据、进行格式化处理后存储为需要的格式。
2. ***Spider_UI.py***。图形化界面，以每篇保存的帖子为间隔展示输入的所有帖子，允许用户选择自己需要的段落并在分类自动格式化处理后保存。
3. ***Fliter.py***。辅助用，自动处理输入的文件，根据输入的参数选择删除文件的重复url还是删除文件的重复过时帖子。
## 4各部分介绍及使用方法
###**4.1【写在前面】：**
> 由于系统自动化程序不够完全，建议将每个.py文件在命令行中手动运行，方法见下方 **4.2【推荐的使用方法】**。 
>  
###**4.2【推荐的使用方法】：**
1. 自己保存关注的链接到文件中，例如命名为 ***data.txt***，内容格式例如：
```
【社招】【小红书】信息流广告算法，点击查看：https://bbs.byr.cn/article/JobInfo/950789 (来自北邮人论坛)
【校招】【中信信托】2023年校园招聘公告，点击查看：https://bbs.byr.cn/article/JobInfo/950793 (来自北邮人论坛)
```
1. 在命令行中输入 ```python Spider_Analyser.py data.txt``` ，输出结果见下面的 **4.3【文件说明】**。一般来说会有两个文件 ***日期_Others.txt*** 和 ***日期_Whisper.txt***，第一个文件只含有不属于"悄悄话"帖子的URL链接，第二个文件是"悄悄话"帖子的内容。**【注：如果你没有下面那些需求，完全可以从本步骤完成后跳到第六步。】**
2. 如果需要获取不属于"悄悄话"帖子的内容，可以继续输入 ```python Spider_Others.py 日期_Others.txt```，会生成 ***日期_Others.txt*** 文件，保存这些帖子的内容。
3. 由于悄悄话可能在抓取内容后有新的回复，程序会自动将可能有新回复的链接存于 ***日期_Whisper_Updating.txt*** 中，需要由用户等待一段时间后（一般不会超过一天），手动输入 ```python Spider_Analyser.py 日期_Whisper_Updating.txt```，重新获取帖子的内容，结果延续上次抓取的结果保存在 ***日期_Whisper.txt*** 中。
4. 因为第三步的存在，可能会导致一个帖子被爬取多次的情况，此时可以在命令行输入 ```python Fliter.py 日期_Whisper.txt 0```，将 ***日期_Whisper_Updating.txt*** 去重后保留最新一次爬取的内容，对于 ***日期_Others.txt*** ，也有相似处理。也可以在命令行中输入 ```python Fliter.py 日期_Others.txt```，删除 ***日期_Others.txt*** 中重复的URL。更多关于 *Fliter.py* 的说明见下方 **4.3【文件说明】**。
5. 最后是 **图形化人工识别选取所需信息** 部分。 在命令行中输入 ```python Spider_UI.py 日期_Whisper.txt```，即可一张一张帖子浏览并选择性保留你的所需信息。用法见下方文件说明部分。

###**4.3【文件说明】：**
1. ***Spider_Analyser.py*** 和 ***Spier_Others.py***
```
Spider_Analyser.py
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
#
#   输出：
#       1.正常运行：一般输出两个文件"日期_Others.txt"和"日期_Whisper.txt"
#         如果 Whisper中有近期回复的帖子，额外输出文件"日期_Whisper_Updating.txt"
#       2.运行错误中途退出：除去上述文件，额外存在文件"日期_TmpSave.txt"
#       3.其他：如果帖子已经被删帖而无法访问网页，会生成"error.txt"文件
```
```
Spier_Others.py
# 说明：
#   输入：
#       命令行执行时，输入保存待分析网页数据的文件名作为第一个参数，输入文件后缀名应该为.txt
#
#   程序执行：
#       1.从输入文件按行提取出网址保存到列表 Whisper，生成用于处理错误的"日期_TmpSave.txt"文件
#       2.利用selenium，抓取 Whisper中每个帖子的所需信息，处理后存储在"日期_Others.txt"中
#       3.一切运行结束后，删除临时文件"日期_TmpSave.txt"
#
#   输出：
#       1.正常运行：一般输出文件"日期_Others.txt"，保存帖子信息
#       2.运行错误中途退出：除去上述文件，额外存在文件"日期_TmpSave.txt"
#       3.其他：如果帖子已经被删帖而无法访问网页，会生成"error.txt"文件
```
2. ***Spider_UI.py***
```
# 说明：
#   输入：
#       命令行执行时，输入保存待分析帖子所在的文件名作为第一个参数，输入文件后缀名应该为.txt
#
#   程序使用：
#       1.打开后，会产生一个GUI图形化界面，主体的左侧是一个表格，右侧是一个文本框
#       2.左侧表格会显示输入文件的帖子的内容（一篇），右侧文本框显示用户在左侧表格选择的行经处理后的结果
#       3.其中，表格会自动高亮发帖人的名字，且涂黑评论间的分割字段
#       4.而文本框则可以任意修改内容，但我们真诚建议不要删去它的分割行，否则保存会出错
#       5.文本标签栏（通常显示为"工作/Ctrl+S"），意为选择您对本帖子的情感倾向
#       6.按下'Ctrl+S'可以修改文本标签栏，依次在工作、情感、疫情、生活、学业间切换
#       7.使用时，可以通过按住'Ctrl+鼠标左键'选择一行的方法选中多行文本
#       8.注意，选中一行会自动选择该评论相关的所有行，因此，建议点击分割行来选取某评论
#       9.选中后，按下"开始"按钮/'Ctrl+A'，文本框会自动显示所选行分析后的结果
#      10.按下"下一个"按钮/'Ctrl+D'，会切换到下个帖子，并自动分析全帖，显示在右侧文本框中
#      11.按下"保存"按钮/'Ctrl+W'，程序会在删除评论时间和评论人等信息后，格式化保存右侧文本框内容到"文本标签栏_result.txt"文件中
#      12."统计结果"按钮没有用，请不要在意
#      13.程序会自动生成"源文件名-1.txt"，它保存了您最后一次点击"保存"后还未分析的帖子的内容
#      14.它也可以帮助您在下一次打开本程序后跳过已分析的帖子，自动展示还未分析的第一篇帖子
#      15.建议在不需要后（比如分析完整个文件），将其手动删除
#      16.它也可以在您点击"下一个"按钮后，发现提示'文档已到末尾'后，自动删除
#
#   输出：
#       1.正常执行后，会产生文件"源文件名-1.txt"和若干（最多5种）形似"Job_result.txt"，
#           其中Job可以被替换为Life、Emotion、Epidemic、Study
#       2.如果是在使用中，点击"下一个"按钮后，发现提示'文档已到末尾'，则不存在"源文件名-1.txt"
```
3. ***Fliter.py***
```
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
```
## 5未来更新计划
1. 本意是想把整个爬虫放在租的服务器上定时运行的，但现在 **单个程序的鲁棒性测试** 和 **整个统筹工具的逻辑** 都还没做，需要完善。（至少让它在除了图形化这部分必须人工完成外能连贯运作，形成自动化系统）
2. 如果要部署在服务器的话，和用户之间的通信（指感兴趣帖子链接的传输和爬取结果的返回）可以通过 **邮件** 来实现，代码我已经有了，但要在第一步的基础上完成。
3. 现在链接还要我个人手动获取，属实太慢了，等我进修完成，看看能否使用 **NLP/其他人工智能技术**，回顾学习的《信息与知识获取课程》和《Linux开发环境即应用》，训练一个可以自动寻获感兴趣帖子的模型。 
4. 今年顺便租了个数据库，看看能不能将得到的信息整理到 **数据库** 上面去，练习数据库的使用方式。
5. 禁忌的技术：在本项目基础上，可以实现一些其他东西，不便细说。
6. 使用Json格式，以便处理

## 6个人总结
1. 这是自己给自己的一个**项目驱动型学习**，感觉非常充实，精神不再空虚，缺点就是期间没太锻炼。可以修整片刻后继续。
2. 学习了很多技术。**selenium方面**，包括基础应用、移动端模拟、前端网页元素的定位CSS_SELECTOR（类似SQL嵌套查询的思路）、按键模拟等；**PyQt5方面**，包括基础页面布局的设置，QWidget、QMessageBox、QLineEdit、QLabel、QTableWidget、QTextEdit、全局快捷键的设置、信号与槽的机制、函数绑定、自动计时器实现类的扩充等；**此外**，我还复习了Re正则匹配库、Python基础语法尤其是列表、字典、类及其成员函数的撰写、try except（虽然还需要系统学一遍，现在学的都是实践应用逐渐摸索起来的）、OS库与命令行的基本交互、**对**诸如状态机思想的应用、变量命名、注释规范与语言表达、自动化处理、软件测试及错误处理、需求分类及设计扩展统一、临时文件的意义、与用户的交互的模式设计有了**更深的领悟**。
3. 其他还有很多学习但没有用到的知识、例如PyQt中创建与管理多线程（尤其单例模式）、跨线程通信、自动发送邮件、JSON格式的存读、Python导入自己写的包等（我是从学习别的项目视频入的门，虽然最后发现这个项目视频是盗的别人的...[学习的项目的链接](https://www.bilibili.com/video/BV1X14y1V741?p=1&vd_source=e5484c76146fb4caa047e387173000ff))

[^1]:每天500-600个，巅峰超过1k个
[^2]:实际本项目的爬虫频率2s/次，可以自主修改
[^3]:由于是模拟人的点击来操作，所以实际上被反爬的概率将大大降低。selenium能够执行页面上的js，对于js渲染的数据和模拟登陆处理起来非常容易。
