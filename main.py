import sys
from PyQt5 import QtWidgets
from window import Dytt_Window

if __name__ == '__main__':
    print("开始运行")
    # 窗口显示
    app = QtWidgets.QApplication(sys.argv)
    # 实例化一个窗口对象
    window = Dytt_Window()
    window.show()
    sys.exit(app.exec_())
