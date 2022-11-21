# 目标：
#   图形化界面，以每篇保存的帖子为间隔展示输入的所有帖子，允许用户选择自己需要的段落并在分类格式化处理后保存

# version：1.0
# Author：SwordLikeRain
# Date：2022.11.21

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
#
# 其他说明：
#   本代码中，以行为界划分每张帖子，在实践过程中，
#   发现存在可能更合理的数据结构：以条来划分，一条评论是一部分，这样有利于实现更多功能。如有余力，可以考虑

import sys
import os
import re
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QLabel, QTextEdit
from PyQt5.QtWidgets import QMessageBox, QMenu, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtWidgets
from PyQt5 import QtGui

# 文本标签栏的可能状态
STATE_DIC = {
    0: {'C': "工作", 'E': "Job"},
    1: {'C': "情感", 'E': "Emotion"},
    2: {'C': "疫情", 'E': "Epidemic"},
    3: {'C': "生活", 'E': "Life"},
    4: {'C': "学业", 'E': "Study"},
}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 绑定控件
        self.table = None  # 表格
        self.text_edit = None  # 文本框
        self.file_text = None  # 读取的文件内容
        self.lbl_state = None  # 文本倾向标签栏

        # 共享变量
        self.total_line = 0  # 文件总行数
        self.next_line = 0  # 文件该处理的下一行的行号
        self.show_list = []  # 文本框内容
        self.state = 1  # 标签状态

        self.Author = ''  # 帖子发帖人名称
        self.line_start = []  # 定位表，存储当前在'表格'中的帖子的评论的开始行，同时存储0代表问题开始行

        # 标题\尺寸设置
        self.setWindowTitle('文字筛选处理器')
        self.resize(3000, 1500)

        # 窗体位置
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

        # 窗体设置元素的排列方式
        layout = QVBoxLayout()  # 垂直方向布局
        layout.addLayout(self.init_table())
        layout.addLayout(self.init_footer())
        self.setLayout(layout)

        # 启动函数，初始化页面
        self.read_file()
        self.set_shortcut()
        self.event_next_click()

    # 从命令行获取文件名，按行读取文件内容形成列表存于file_text中，同时为自动跳转到上一次工作结束位置铺垫
    def read_file(self):
        # 1.按行读取文件内容形成列表存于file_text中
        with open("{}".format(sys.argv[1]), 'r', encoding='utf-8') as f:
            self.file_text = f.read().splitlines()
            self.total_line = len(self.file_text)
        
        # 2.延续上一次未完成的处理工作
        #   思路：如果上一次已经处理过这个文件，读取上一次保存的最后一个帖子的下一个帖子行号存储在next_line中
        #         因为如果处理过这个文件，会在"文件名-1.txt"文件的第一行存储下一个帖子的行号
        if os.path.exists("{}".format(sys.argv[1])[:-4]+'-1.txt'):
            with open("{}".format(sys.argv[1])[:-4]+'-1.txt', 'r', encoding='utf-8') as f:
                self.next_line= int(f.readline().strip())

    # 绑定快捷键
    def set_shortcut(self):

        QShortcut(QKeySequence("Ctrl+D"),
                  self).activated.connect(lambda: self.event_next_click())
        QShortcut(QKeySequence("Ctrl+W"),
                  self).activated.connect(lambda: self.event_save_click())
        QShortcut(QKeySequence("Ctrl+A"),
                  self).activated.connect(lambda: self.event_start_click())
        QShortcut(QKeySequence("Ctrl+S"),
                  self).activated.connect(lambda: self.change_state())

    # 布局表格和文本框
    def init_table(self):
        table_layout = QHBoxLayout()

        # 1.创建表格
        self.table = table = QTableWidget(0, 1)  # 绑定控件，默认几行几列
        table.setColumnWidth(0, 1400) # 设置表格显示大小
        table.cellPressed.connect(self.auto_select)  # 绑定自动多选函数
        item = QTableWidgetItem()
        item.setText('内容')
        table.setHorizontalHeaderItem(0, item) # 设置表头
        table_layout.addWidget(table)

        # 2.创建右侧笔记
        self.text_edit = text_edit = QTextEdit()
        text_edit.setFontPointSize(12) # 设置显示字号大小
        table_layout.addWidget(text_edit)

        return table_layout

    # 布局四个按钮和一个文本标签栏
    def init_footer(self):
        footer_layout = QHBoxLayout()

        btn_start = QPushButton("开始/Ctrl+A")
        btn_start.clicked.connect(self.event_start_click)
        footer_layout.addWidget(btn_start)

        footer_layout.addStretch()
        self.lbl_state = lbl_state = QLabel("工作/Ctrl+S", self)
        footer_layout.addWidget(lbl_state)

        btn_next = QPushButton("下一个/Ctrl+D")
        btn_next.clicked.connect(self.event_next_click)
        footer_layout.addWidget(btn_next)

        btn_save = QPushButton("保存/Ctrl+W")
        btn_save.clicked.connect(self.event_save_click)
        footer_layout.addWidget(btn_save)

        btn_statistics = QPushButton("统计结果") # 这个没写完，不想写了
        # btn_statistics.clicked.connect(self.event_statistics_click)
        footer_layout.addWidget(btn_statistics)

        return footer_layout

    # 在表格中选中某行后，自动选择该行所在评论的所有行（应用时建议选择每条评论的最后一行）
    # 输入为用户在图形化界面表格中选中表格的行号和列号
    def auto_select(self, row, col):
        try:
            # start_line和 end_line为这条评论在表格中的开始和结束行号
            for i in self.line_start:
                if i > row:
                    end_line = i - 1
                    break
                start_line = i

            self.table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection) # 允许多选
            for i in range(start_line, end_line):
                self.table.selectRow(i)
            self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # 关闭多选
        except:
            pass

    # Ctrl+S 改变文本标签栏
    def change_state(self):
        self.state = (self.state + 1) % len(STATE_DIC)
        self.lbl_state.setText(STATE_DIC[self.state]['C']+'/Ctrl+S')

    # Ctrl+A 开始分析选中行，呈现在右侧文本框中
    def event_start_click(self):
        # 1.获取选中表格的行号形成列表row_list
        row_list = self.table.selectionModel().selectedRows()
        num = []
        for row in row_list:
            num.append(row.row())

        # 2.分析选中行，呈现在右侧文本框中
        self.fflush(num)

    # Ctrl+D 切换到下个帖子，并自动分析全帖，显示在右侧文本框中
    def event_next_click(self):

        # 1.输出警告框：已经最后一个文档了
        if self.next_line == self.total_line:
            if os.path.exists("{}".format(sys.argv[1])[:-4]+'-1.txt'):
                os.remove("{}".format(sys.argv[1])[:-4]+'-1.txt')
            QMessageBox.warning(self, '错误', '文档已到末尾')
            return

        # 2.左侧表格内容清空来初始化，同时发帖人字段也清空
        for i in range(self.table.rowCount()):  # 清空列表，注意删除的是第0行
            self.table.removeRow(0)
        self.Author = ''

        # 3.清空帖子的定位表，它存储当前在'表格'中的帖子的评论的开始行，同时存储0代表问题开始行
        self.line_start.clear()
        self.line_start.append(0)

        # 4.获取新帖子内容，存在左侧表格中
        content = self.file_text[self.next_line]  # 一行内容
        self.next_line += 1
        row_count = 0  # 表格中将添加的下一行的行号
        while self.next_line < self.total_line:
            # *1.换帖行
            if content == '---------------------------------------------------------------------------------------------------------------------------------------------------':
                self.line_start.append(row_count+1) # 加入虚拟的额外评论的开始行，以便处理

                # 表格中添加评论分隔行，便于用户选中
                self.table.insertRow(row_count)
                cell = QTableWidgetItem('---------------------------')
                self.table.setItem(row_count, 0, cell)
                cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                cell.setBackground(QtGui.QColor(0, 0, 0))
                cell.setForeground(QtGui.QColor(0, 0, 0))
                break
            # 表格中添加新行，设置内容为读取文件行的内容
            self.table.insertRow(row_count)  # 表格添加一行
            cell = QTableWidgetItem(content)
            self.table.setItem(row_count, 0, cell) # 添加该行元素 cell
            cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # 设置为不可编辑
            
            # *2.修改发帖人的名字，使其为红色高亮，便于用户阅读
            if self.Author == content.strip() and len(self.Author) != 0: 
                cell.setForeground(QtGui.QColor(255, 0, 0))

            # *3.首次发现发帖人的名字，将其保存在 self.Author中，并设置为红色高亮，便于用户阅读
            if content[0:2] == 'T：':
                self.table.item(row_count-1, 0).setForeground(QtGui.QColor(255, 0, 0))
                self.Author = self.table.item(row_count-1, 0).text().strip()

            # *4.评论的分割行，全涂黑以便用户阅读，并将其下一行添加到评论的开始行中
            if content == '---------------------------':
                self.line_start.append(row_count+1)
                cell.setBackground(QtGui.QColor(0, 0, 0))
                cell.setForeground(QtGui.QColor(0, 0, 0))

            content = self.file_text[self.next_line]  # 一行内容
            self.next_line += 1
            row_count += 1

        # 4.自动在右侧文本框分析表格内容并显示
        self.fflush(list(range(1, self.table.rowCount())))

    # Ctrl+W 删除冗余信息后，格式化保存右侧文本框内容到"文本标签栏_result.txt"文件中
    # 更新备份文件'原文件名-1.txt"，第一行保存下一次处理的帖子的行号，其他行保存未处理的帖子的信息
    # 一切操作成功后，弹出信息框提示且自动关闭
    # 失败则弹出错误警告框
    def event_save_click(self):
        try:
            # 1.格式化保存信息，只保存评论内容，忽略时间和评论人等信息
            # save_content = self.text_edit.toPlainText()
            with open(STATE_DIC[self.state]['E']+"_result.txt", 'a', encoding='utf-8') as f:
                Q_is_here = False
                for s in self.show_list:
                    if s == '---------------------------\n':
                        Q_is_here = False
                    elif s[0:2] in ['T：', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8','A9']:
                        Q_is_here = True
                    if Q_is_here:
                        f.write(s)
                f.write(
                    '------------------------------------------------------------------------------------------\n')

            # 2.更新备份文件'原文件名-1.txt"，第一行保存下一次处理的帖子的行号，其他行保存未处理的帖子的信息
            #   保存成功弹出信息框提示且自动关闭
            with open("{}".format(sys.argv[1])[:-4]+'-1.txt', 'w', encoding='utf-8') as f:
                f.write(str(self.next_line)+'\n') # 保存下一次处理的帖子的行号
                i = self.next_line
                while i < self.total_line:
                    f.write(self.file_text[i]+'\n')
                    i += 1
            msg = TimerMsgBox(500)
        except:
            QMessageBox.warning(self, "错误", "保存失败，请重新尝试")

    def event_statistics_click(self):
        pass

    # 自动分析表格中已经选择行的内容，将生成结果显示在右侧文本框
    # 输入参数为表格中选中的行的行号形成的列表
    def fflush(self, row_list):

        # 1.排序要展示的行号，清空右侧文本框
        row_list.sort()
        self.show_list.clear()

        # 2.设置变量
        answer_seq = 1  # 下一个答案的编号
        next_is_reply = False  # 下一行是否为回复（是否要开始回复处理）
        reply_is_over = False  # 回复处理是否结束
        reply_seq = 0  # 带回复的评论的开始行号

        # 3.开始处理
        for row in row_list:  # 得到行号row
            text = self.table.item(row, 0).text()  # 获取该行内容

            # 评论分界符，重置Flag状态
            if text == '---------------------------':  
                next_is_reply = False
                reply_is_over = False
                self.show_list.append(text+'\n')
                continue

            # 开始回复处理，找到回复的是第几条答案，并将其加在reply_seq行评论的Re部分
            elif next_is_reply:  
                if reply_is_over: # 回复处理已完成，剩下的都是引用的字段，可以无视
                    continue
                ans_row = 0  # 被引用的评论的开始行号
                answer_name = ''  # 被引用的评论人的评论的答案编号
                while ans_row < len(self.show_list):
                    if self.show_list[ans_row][0] == 'A' or self.show_list[ans_row][0] == 'Q':
                        answer_name = re.search(
                            '(A[0-9]+)|Q', self.show_list[ans_row]).group()
                    if text[2:] in self.show_list[ans_row]:
                        break
                    ans_row += 1
                # 运行到这里，要么ans_row是被引用的评论所在行，要么没找到其所在行，有ans_row=len(self.show_list)
                # 被引用所在行是'Q'不管，如果因为没有在表格中选中，所以找不到被引用评论所在行也不管
                if answer_name != 'Q' and ans_row != len(self.show_list):
                    # reply_head是引用者的评论的开始行的内容，要给这行添加Re
                    reply_head = self.show_list[reply_seq]
                    start_pos = len(str(answer_seq-1))+1
                    self.show_list[reply_seq] = reply_head[:start_pos] + \
                        '（Re：'+answer_name+'）'+reply_head[start_pos:]
                reply_is_over = True
                
            # 给答案行加上答案编号
            elif text[0] == 'A':  
                self.show_list.append('A' + str(answer_seq) + text[1:]+'\n')
                answer_seq += 1

            # 下一行是回复引用，从后往前遍历已经保存的评论，找到引用者的评论的开始行号（就是最新保存的评论），存于reply_seq中（可以考虑用line_start实现）
            elif text[0] == '【':  
                next_is_reply = True # 下一次就是回复处理
                reply_seq = len(self.show_list) - 1
                while reply_seq >= 0:
                    if self.show_list[reply_seq][0] == 'A':
                        break
                    reply_seq -= 1
                continue

            elif len(text.strip()) != 0:
                self.show_list.append(text+'\n')

        # 4.将结果合并成一个字符串，显示在文本框中
        result_str = ''
        for s in self.show_list:
            result_str += s
        self.text_edit.setText(result_str)

# class TimerMsgBox(QMessageBox):
#     def __init__(self, timeout):
#         super().__init__()
#         self.timeout=timeout

#         self.setWindowTitle("成功")
#         self.setText("保存成功")

#         self.timer = QTimer(self)
#         self.timer.setInterval(200)
#         self.timer.timeout.connect(self.timerout)
#         self.timer.start()

#         self.exec_()
        
#     def timerout(self):
#         self.timeout-=100
#         if self.timeout <=0:
#             self.close() # self指TimerMsgBox

#     def closeEvent(self,event):
#         self.timer.stop()
#         event.accept() # 触发接受信号

# 设置一个根据timeout时间自动关闭的MessageBox，二选一都可以用，但前者是异步的思路（虽然实践感觉好像没啥用？）
# 输入参数 timeout指延迟自动关闭的时间
class TimerMsgBox(QMessageBox):
    def __init__(self, timeout):
        super().__init__()
        self.timeout = timeout
        self.setWindowTitle("成功")
        self.setText("保存成功")
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        # self.setDefaultButton(QMessageBox.Ok)
        self.button(QMessageBox.Ok).animateClick(timeout)
        self.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
