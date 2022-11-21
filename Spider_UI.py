# 本代码中，以行为划分每张帖子，然后在实践过程中，发现存在更合理的数据结构：以条来划分，一条评论是一部分，这样有利于实现更多功能。如有余力，可以考虑

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
        self.lbl_state = None  # 文本倾向标签

        self.total_line = 0  # 文件总行数
        self.next_line = 0  # 该处理的下一行的行号
        self.show_list = []  # 存储文本框列表
        self.state = 1  # 标签状态

        self.Author = ''  # 帖子发帖人名称
        self.line_start = []  # 定位表，存储每个帖子的评论开始行

        # 标题\尺寸
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

    def read_file(self):
        # 读取文件内容，按行形成列表存于file_text中

        # with open("20221118_Whisper.txt", 'r', encoding='utf-8') as f:
        with open("{}".format(sys.argv[1]), 'r', encoding='utf-8') as f:
            self.file_text = f.read().splitlines()
            self.total_line = len(self.file_text)
        
        if os.path.exists("{}".format(sys.argv[1])[:-4]+'-1.txt'):
            with open("{}".format(sys.argv[1])[:-4]+'-1.txt', 'r', encoding='utf-8') as f:
                self.next_line= int(f.readline().strip())

    def set_shortcut(self):
        # 绑定快捷键

        QShortcut(QKeySequence("Ctrl+D"),
                  self).activated.connect(lambda: self.event_next_click())
        QShortcut(QKeySequence("Ctrl+W"),
                  self).activated.connect(lambda: self.event_save_click())
        QShortcut(QKeySequence("Ctrl+A"),
                  self).activated.connect(lambda: self.event_start_click())
        QShortcut(QKeySequence("Ctrl+S"),
                  self).activated.connect(lambda: self.change_state())

    def init_table(self):
        # 设置表格和布局
        table_layout = QHBoxLayout()

        # 1.创建表格
        self.table = table = QTableWidget(0, 1)  # 绑定控件，默认几行几列
        table.setColumnWidth(0, 1400)
        table.cellPressed.connect(self.auto_select)  # 绑定自动多选函数
        item = QTableWidgetItem()
        item.setText('内容')
        table.setHorizontalHeaderItem(0, item)

        table_layout.addWidget(table)

        # 2.创建右侧笔记
        self.text_edit = text_edit = QTextEdit()
        text_edit.setFontPointSize(12)
        table_layout.addWidget(text_edit)

        return table_layout

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

        btn_statistics = QPushButton("统计结果")
        # btn_statistics.clicked.connect(self.event_statistics_click)
        footer_layout.addWidget(btn_statistics)

        return footer_layout

    def auto_select(self, row, col):
        # 选中某行后，自动选择该行相关评论的所有行
        try:
            for i in self.line_start:
                if i > row:
                    end_line = i - 1
                    break
                start_line = i

            self.table.setSelectionMode(
                QtWidgets.QAbstractItemView.MultiSelection)
            for i in range(start_line, end_line):
                self.table.selectRow(i)
            self.table.setSelectionMode(
                QtWidgets.QAbstractItemView.ExtendedSelection)
        except:
            pass

    def change_state(self):
        # Ctrl+S 改变文本标签
        self.state = (self.state + 1) % len(STATE_DIC)
        self.lbl_state.setText(STATE_DIC[self.state]['C']+'/Ctrl+S')

    def event_start_click(self):
        # 1.获取选中表格的行号形成列表row_list
        row_list = self.table.selectionModel().selectedRows()
        num = []
        for row in row_list:
            num.append(row.row())

        # 2.分析选中行，呈现在右侧文本框中
        self.fflush(num)

    def event_next_click(self):

        # 1.警告，已经最后一个文档了
        if self.next_line == self.total_line:
            QMessageBox.warning(self, '错误', '文档已到末尾')
            return

        # 2.左侧表格内容清空来初始化，同时作者字段也清空
        for i in range(self.table.rowCount()):  # 清空列表，注意删除的是第0行
            self.table.removeRow(0)
        self.Author = ''

        # 3.清空帖子的定位表
        self.line_start.clear()
        self.line_start.append(0)

        # 4.获取新帖子内容，存在左侧表格中
        content = self.file_text[self.next_line]  # 一行内容
        self.next_line += 1
        row_count = 0  # 表格中将添加的下一行行号
        while self.next_line < self.total_line:
            if content == '---------------------------------------------------------------------------------------------------------------------------------------------------':
                self.line_start.append(row_count+1)

                self.table.insertRow(row_count)  # 添加新行
                cell = QTableWidgetItem('---------------------------')
                self.table.setItem(row_count, 0, cell)
                cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                break
            self.table.insertRow(row_count)  # 添加新行
            cell = QTableWidgetItem(content)
            self.table.setItem(row_count, 0, cell)
            cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            if self.Author == content.strip() and len(self.Author) != 0:
                cell.setForeground(QtGui.QColor(255, 0, 0))
            if content[0:2] == 'T：':
                self.table.item(
                    row_count-1, 0).setForeground(QtGui.QColor(255, 0, 0))
                self.Author = self.table.item(row_count-1, 0).text().strip()
            if content == '---------------------------':
                self.line_start.append(row_count+1)
                cell.setBackground(QtGui.QColor(0, 0, 0))
                cell.setForeground(QtGui.QColor(0, 0, 0))

            content = self.file_text[self.next_line]  # 一行内容
            self.next_line += 1
            row_count += 1

        # 4.自动在右侧文本框分析表格内容并显示
        self.fflush(list(range(1, self.table.rowCount())))

    def event_save_click(self):
        try:
            # 1.格式化保存信息
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

            # 2.更新源文件
            # with open("20221118_Whisper-1.txt", 'w', encoding='utf-8') as f:
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

    def fflush(self, row_list):

        # 排序要展示的行号，清空右侧文本框
        row_list.sort()
        self.show_list.clear()

        answer_seq = 1  # 下一个答案的编号
        next_is_reply = False  # 下一行是否为回复（是否要开始回复处理）
        reply_is_over = False  # 回复处理是否结束
        reply_seq = 0  # 带回复的评论的开始行号

        for row in row_list:  # 得到行号
            text = self.table.item(row, 0).text()  # 获取该行内容

            if text == '---------------------------':  # 评论分界符，重置Flag状态
                next_is_reply = False
                reply_is_over = False
                self.show_list.append(text+'\n')
                continue
            elif next_is_reply:  # 处理回复评论的评论，找到回复的是第几条答案，并将其加在reply_seq行评论的Re部分
                if reply_is_over:
                    continue
                ans_row = 0  # 回答所在行
                answer_name = ''  # 回答人的答案编号
                while ans_row < len(self.show_list):
                    if self.show_list[ans_row][0] == 'A' or self.show_list[ans_row][0] == 'Q':
                        answer_name = re.search(
                            '(A[0-9]+)|Q', self.show_list[ans_row]).group()
                    if text[2:] in self.show_list[ans_row]:
                        break
                    ans_row += 1
                # 运行到这里，要么ans_row是回答所在行，要么没找到回答所在行，ans_row=len(self.show_list)
                # 回答行是'Q'不管，找不到对应回答也不管
                if answer_name != 'Q' and ans_row != len(self.show_list):
                    # reply_head是评论头所在行，要给这行添加Re
                    reply_head = self.show_list[reply_seq]
                    start_pos = len(str(answer_seq-1))+1
                    self.show_list[reply_seq] = reply_head[:start_pos] + \
                        '（Re：'+answer_name+'）'+reply_head[start_pos:]
                reply_is_over = True
            elif text[0] == 'A':  # 给答案加上编号
                self.show_list.append('A' + str(answer_seq) + text[1:]+'\n')
                answer_seq += 1
            elif text[0] == '【':  # 下一行是回复，从后往前遍历已经保存的答案，找到这个带回复的评论的开始行号，存于reply_seq中（可以考虑用line_start实现）
                next_is_reply = True
                reply_seq = len(self.show_list) - 1
                while reply_seq >= 0:
                    if self.show_list[reply_seq][0] == 'A':
                        break
                    reply_seq -= 1
                continue
            elif len(text.strip()) != 0:
                self.show_list.append(text+'\n')

        result_str = ''
        for s in self.show_list:
            result_str += s
        self.text_edit.setText(result_str)

# 设置一个根据timeout时间自动关闭的MessageBox，二选一都可以用，但前者是异步的思路（虽然实践感觉好像没啥用？）

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
#             self.close()

#     def closeEvent(self,event):
#         self.timer.stop()
#         event.accept()

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
