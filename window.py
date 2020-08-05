import re
import threading
from spider import spider
from PyQt5 import QtWidgets
from DyttSpiderUI import Ui_MainWindow
import inspect
import ctypes

# 电影数据的筛选规则
class stPercolator:
    def __init__(self):
        self.type = []      # 电影类型(队列)
        self.country = []   # 电影产地(队列)
        self.age = []       # 电影年代(队列)
        self.rating = ""    # 电影评分(字符串)
        self.page = ""      # 爬虫页码(字符串)
        self.length = ""    # 电影片长(字符串)

class stMovieInfos:
    def __init__(self):
        self.total = 0      # 电影总数
        self.current = 0    # 当前在第几部电影
        self.tittle = ""    # 当前电影tittle
        self.value = 0      # 符合条件的电影数
        self.finish = False # 爬虫结束标志位

class Dytt_Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # 初始化配置
        super().__init__()
        self.setupUi(self)
        self.init()

    def init(self):
        # 默认开始/停止button是等待打开的状态
        self.button_status = True
        # 默认"类型"框选择"ALL"
        self.checkBox.setChecked(True)
        # 反灰"类型"框的其他checkbox
        self.type_other_checkbox_grid(False)
        # 默认"地区"框选择"ALL"
        self.checkBox_12.setChecked(True)
        # 反灰"地区"框的其他checkbox
        self.area_other_checkbox_grid(False)
        # 默认"年代"框选择"ALL"
        self.checkBox_23.setChecked(True)
        # 反灰"年代"框的其他checkbox
        self.age_other_checkbox_grid(False)
        # 按键的背景颜色为白色
        self.pushButton.setStyleSheet("background-color: white")
        # 开始/取消button
        self.pushButton.clicked.connect(self.start_cancel_button)
        # "类型"框的"ALL"button
        self.checkBox.clicked.connect(self.type_all_checkbox)
        # "地区"框的"ALL"button
        self.checkBox_12.clicked.connect(self.area_all_checkbox)
        # "年代"框的"ALL"button
        self.checkBox_23.clicked.connect(self.age_all_checkbox)
        # 爬虫进度显示”等待开始“
        self.label_5.setText("等待开始。。。")
        # 初始化进度条: 0%
        self.progressBar.setValue(0)

    # 获取"类型"框筛选规则
    def get_type_rule(self):
        type = []
        if self.checkBox.isChecked():
            type.append(self.checkBox.text())
        if self.checkBox_2.isChecked():
            type.append(self.checkBox_2.text())
        if self.checkBox_3.isChecked():
            type.append(self.checkBox_3.text())
        if self.checkBox_4.isChecked():
            type.append(self.checkBox_4.text())
        if self.checkBox_5.isChecked():
            type.append(self.checkBox_5.text())
        if self.checkBox_6.isChecked():
            type.append(self.checkBox_6.text())
        if self.checkBox_7.isChecked():
            type.append(self.checkBox_7.text())
        if self.checkBox_8.isChecked():
            type.append(self.checkBox_8.text())
        if self.checkBox_9.isChecked():
            type.append(self.checkBox_9.text())
        if self.checkBox_10.isChecked():
            type.append(self.checkBox_10.text())
        if self.checkBox_11.isChecked():
            type.append(self.checkBox_11.text())
        return type

    # 获取"地区"框筛选规则
    def get_area_rule(self):
        area = []
        if self.checkBox_12.isChecked():
            area.append(self.checkBox_12.text())
        if self.checkBox_13.isChecked():
            area.append(self.checkBox_13.text())
        if self.checkBox_14.isChecked():
            area.append(self.checkBox_14.text())
        if self.checkBox_15.isChecked():
            area.append(self.checkBox_15.text())
        if self.checkBox_16.isChecked():
            area.append(self.checkBox_16.text())
        if self.checkBox_17.isChecked():
            area.append(self.checkBox_17.text())
        if self.checkBox_18.isChecked():
            area.append(self.checkBox_18.text())
        if self.checkBox_19.isChecked():
            area.append(self.checkBox_19.text())
        if self.checkBox_20.isChecked():
            area.append(self.checkBox_20.text())
        if self.checkBox_21.isChecked():
            area.append(self.checkBox_21.text())
        if self.checkBox_22.isChecked():
            area.append(self.checkBox_22.text())
        return area

    # 获取"年代"框筛选规则
    def get_age_rule(self):
        age = []
        if self.checkBox_23.isChecked():
            age.append(self.checkBox_23.text())
        if self.checkBox_24.isChecked():
            age.append(self.checkBox_24.text())
        if self.checkBox_25.isChecked():
            age.append(self.checkBox_25.text())
        if self.checkBox_26.isChecked():
            age.append(self.checkBox_26.text())
        if self.checkBox_27.isChecked():
            age.append(self.checkBox_27.text())
        if self.checkBox_28.isChecked():
            age.append(self.checkBox_28.text())
        if self.checkBox_29.isChecked():
            age.append(self.checkBox_29.text())
        if self.checkBox_30.isChecked():
            age.append(self.checkBox_30.text())
        if self.checkBox_31.isChecked():
            age.append(self.checkBox_31.text())
        return age

    # 获取"评分"框筛选规则
    def get_rating_rule(self):
        # 获取框里的字符串
        str = self.comboBox.currentText()
        # 删除‘>’和空字符
        rating = str.replace('>', "").strip()
        # 返回处理后的字符串
        return rating

    # 获取"页码"框筛选规则
    def get_page_rule(self):
        # 获取框里的字符串
        str = self.comboBox_2.currentText()
        # 删除‘页’和空字符
        page = str.replace('页', "").strip()
        # 返回处理后的字符串
        return page

    # 获取"片长"框筛选规则
    def get_length_rule(self):
        # 获取框里的字符串
        str = self.comboBox_3.currentText()
        # 删除带有"超长常规短片()"的字符串和空字符
        length = re.sub('[超长常规短片()]', '', str).strip()
        return length

    # 获取筛选规则
    def get_rules(self):
        # 定义结构对象
        stPer = stPercolator()
        # 获取各种筛选规则
        stPer.type = self.get_type_rule()
        stPer.country = self.get_area_rule()
        stPer.age = self.get_age_rule()
        stPer.rating = self.get_rating_rule()
        stPer.page = self.get_page_rule()
        stPer.length = self.get_length_rule()
        # 返回规则
        return stPer

    # 开始/取消button的动作函数
    def start_cancel_button(self):
        # 等待开始状态
        if self.button_status:
            self.start_button()
        # 等待取消状态
        else:
            self.cancel_button()

    # 开始button的动作函数
    def start_button(self):
        # 设置button状态为“取消”
        self.pushButton.setText("取消")
        # button背景颜色设置为red
        self.pushButton.setStyleSheet("background-color: red")
        # 更新button状态
        self.button_status = False
        # 初始化进度条: 0%
        self.progressBar.setValue(0)
        # 获取筛选规则
        stPer = self.get_rules()
        # 定义进度条结构体
        stmovie_infos = stMovieInfos()
        # 创建新线程: 启动爬虫
        self.thread_spider = threading.Thread(target=spider, args=(self, stPer, stmovie_infos))
        self.thread_spider.start()

    # 取消button的动作函数
    def cancel_button(self):
        # 取消爬虫函数
        stop_thread(self.thread_spider)
        # 恢复窗口数据：
        # 设置button状态为“开始”
        self.pushButton.setText("开始")
        # button背景颜色设置为white
        self.pushButton.setStyleSheet("background-color: white")
        # 更新button状态
        self.button_status = True
        # 更新进度条状态
        self.progressBar.setValue(0)
        # 爬虫进度显示”等待开始“
        self.label_5.setText("等待开始。。。")

    # “类型”框的ALL的动作函数
    def type_all_checkbox(self):
        # “类型”框的ALL被选中
        if self.checkBox.isChecked():
            # 反灰其他的checkbox
            self.type_other_checkbox_grid(False)
        else:
            # 令其他的checkbox可选
            self.type_other_checkbox_grid(True)

    # 反灰"类型"框除ALL以外的其他checkbox
    def type_other_checkbox_grid(self, status):
        self.checkBox_2.setEnabled(status)
        self.checkBox_3.setEnabled(status)
        self.checkBox_4.setEnabled(status)
        self.checkBox_5.setEnabled(status)
        self.checkBox_6.setEnabled(status)
        self.checkBox_7.setEnabled(status)
        self.checkBox_8.setEnabled(status)
        self.checkBox_9.setEnabled(status)
        self.checkBox_10.setEnabled(status)
        self.checkBox_11.setEnabled(status)
        # 反灰时其他的checkbox更新为不选择False
        if not status:
            self.checkBox_2.setChecked(status)
            self.checkBox_3.setChecked(status)
            self.checkBox_4.setChecked(status)
            self.checkBox_5.setChecked(status)
            self.checkBox_6.setChecked(status)
            self.checkBox_7.setChecked(status)
            self.checkBox_8.setChecked(status)
            self.checkBox_9.setChecked(status)
            self.checkBox_10.setChecked(status)
            self.checkBox_11.setChecked(status)

    # “地区”框的ALL的动作函数
    def area_all_checkbox(self):
        # “地区”框的ALL被选中
        if self.checkBox_12.isChecked():
            # 反灰其他的checkbox
            self.area_other_checkbox_grid(False)
        else:
            # 令其他的checkbox可选
            self.area_other_checkbox_grid(True)

    # 反灰"地区"框除ALL以外的其他checkbox
    def area_other_checkbox_grid(self, status):
        self.checkBox_13.setEnabled(status)
        self.checkBox_14.setEnabled(status)
        self.checkBox_15.setEnabled(status)
        self.checkBox_16.setEnabled(status)
        self.checkBox_17.setEnabled(status)
        self.checkBox_18.setEnabled(status)
        self.checkBox_19.setEnabled(status)
        self.checkBox_20.setEnabled(status)
        self.checkBox_21.setEnabled(status)
        self.checkBox_22.setEnabled(status)
        # 反灰时其他的checkbox更新为不选择False
        if not status:
            self.checkBox_13.setChecked(status)
            self.checkBox_14.setChecked(status)
            self.checkBox_15.setChecked(status)
            self.checkBox_16.setChecked(status)
            self.checkBox_17.setChecked(status)
            self.checkBox_18.setChecked(status)
            self.checkBox_19.setChecked(status)
            self.checkBox_20.setChecked(status)
            self.checkBox_21.setChecked(status)
            self.checkBox_22.setChecked(status)

    # “年代”框的ALL的动作函数
    def age_all_checkbox(self):
        # “年代”框的ALL被选中
        if self.checkBox_23.isChecked():
            # 反灰其他的checkbox
            self.age_other_checkbox_grid(False)
        else:
            # 令其他的checkbox可选
            self.age_other_checkbox_grid(True)

    # 反灰"年代"框除ALL以外的其他checkbox
    def age_other_checkbox_grid(self, status):
        self.checkBox_24.setEnabled(status)
        self.checkBox_25.setEnabled(status)
        self.checkBox_26.setEnabled(status)
        self.checkBox_27.setEnabled(status)
        self.checkBox_28.setEnabled(status)
        self.checkBox_29.setEnabled(status)
        self.checkBox_30.setEnabled(status)
        self.checkBox_31.setEnabled(status)
        # 反灰时其他的checkbox更新为不选择False
        if not status:
            self.checkBox_24.setChecked(status)
            self.checkBox_25.setChecked(status)
            self.checkBox_26.setChecked(status)
            self.checkBox_27.setChecked(status)
            self.checkBox_28.setChecked(status)
            self.checkBox_29.setChecked(status)
            self.checkBox_30.setChecked(status)
            self.checkBox_31.setChecked(status)

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)