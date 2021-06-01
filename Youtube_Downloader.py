# Youtube Downloader
from PyQt5 import QtCore, QtGui, QtWidgets
import threading
# import URL
from pytube import YouTube

lock = threading.Lock()  # threading Lock，避免競速產生
urls, text = [], ""  # urls為影片清單(格式為List)或是單一影片(格式為str)網址， text為GUI網址輸入欄位資料
check = [False]  # 判斷執行續所有執行序是否都已結束
single = False  # 判斷是否為單一影片
playlist = False  # 判斷是否為影片清單
select = ""  # 影片格式選擇的結果
select_video_quality = []  # 影片所支援的Quality
video_type = []  # 判斷是否為影片檔或音源檔
path = ""  # 選擇影片放置的路徑


# 下載前準備
def ready_thread():
    global single, playlist, check, select_video_quality
    if type(urls) == str:
        ui.lineEdit.setEnabled(False)
        single = True
        # print("此網址為單一影片")
        y = YouTube(urls)
        c = y.streams.filter(progressive=True, file_extension="mp4")
        for i in range(len(c)):
            select_video_quality.append(c[i].resolution)
        print(select_video_quality)
        trigger.start()
        demo.show()

    elif type(urls) == list:
        ui.lineEdit.setEnabled(False)
        playlist = True
        check = []
        playlist_reply = QtWidgets.QMessageBox.information(MainWindow, "確認方塊", "是否下載清單內所有影片",
                                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                           QtWidgets.QMessageBox.Yes)
        print(playlist_reply)
        if playlist_reply == QtWidgets.QMessageBox.Yes:
            for u in range(len(urls)):
                check.append(False)
                threading.Thread(target=start_thread, args=(urls[u], u + 1)).start()
            trigger.start()
        else:
            ui.pushButton.setEnabled(True)
            ui.lineEdit.clear()
            print("取消下載")

    single, playlist = False, False


# ----------------開啟執行續----------------------
def start_thread(t, i):
    global check, select_video_quality, video_type, select, path
    if playlist:
        ytd = YouTube(t)
        videos_title = ytd.title
        # ------------------下載中------------------
        lock.acquire()
        k = f"{i:02d}:  {videos_title}......下載中"
        ui.listWidget.addItem(k)
        QtWidgets.QApplication.processEvents()  # 刷新頁面
        print(k)
        lock.release()

        ytd.streams.first().download()
        # -----------------------------------------
        # ----------------下載完成-------------------
        lock.acquire()
        row = i - 1
        check[row] = True
        item = ui.listWidget.takeItem(row)  # 抓取目前欄位(row)，listwidget從第0的row開始。
        ui.listWidget.removeItemWidget(item)  # 刪除目前欄位
        p = f"{i:02d}: ☑ {videos_title}......下載完成"  # 把下載中替換成下載完成
        ui.listWidget.addItem(p)
        QtWidgets.QApplication.processEvents()
        print(threading.active_count())
        print(p)
        lock.release()


    else:
        ytd = YouTube(t)
        videos_title = ytd.title
        if video_type == "影片檔":
            for j in range(len(select_video_quality)):
                if select_video_quality[j] == select:
                    c = ytd.streams.filter(progressive=True, file_extension="mp4")[j]
            # ------------------acquire------------------
            lock.acquire()
            k = f" {videos_title}......下載中"
            ui.listWidget.addItem(k)
            QtWidgets.QApplication.processEvents()  # 刷新頁面
            # print(k)
            lock.release()
            # ------------------release------------------

            # ------------------download------------------
            if path == "":
                c.download()
            else:
                c.download(path)
            # ------------------download------------------

        if video_type == "音源檔":
            c = ytd.streams.filter(only_audio=True, file_extension='mp4').first()
            # ------------------acquire------------------
            lock.acquire()
            k = f" {videos_title}......下載中"
            ui.listWidget.addItem(k)
            QtWidgets.QApplication.processEvents()  # 刷新頁面
            # print(k)
            lock.release()
            # ------------------release------------------

            # ------------------download------------------
            if path == "":
                c.download()
            else:
                c.download(path)
            # ------------------download------------------

        # ------------------acquire------------------
        lock.acquire()
        row = i - 1
        check[row] = True
        item = ui.listWidget.takeItem(row)  # 抓取目前欄位(row)，listwidget從第0的row開始。
        ui.listWidget.removeItemWidget(item)  # 刪除目前欄位
        p = f" ☑ {videos_title}......下載完成"  # 把下載中替換成下載完成
        ui.listWidget.addItem(p)
        ui.lineEdit.clear()
        QtWidgets.QApplication.processEvents()
        # print(p)
        lock.release()
        # ------------------release------------------

    select_video_quality, video_type = [], []
    # print("所有執行續已開啟")


# 完成下載後GUI介面整理，跳出完成下載視窗
def finish_download():
    global check, path
    r = QtWidgets.QMessageBox.about(MainWindow, "完成", "所有影片已經下載完成")
    if r == None:
        ui.lineEdit.clear()
        ui.lineEdit.setEnabled(True)
        ui.listWidget.clear()
        ui.pushButton.setEnabled(True)
        demo.le1.clear()
        demo.le2.clear()
        demo.btn2.setEnabled(False)
        demo.le2.setEnabled(False)
        demo.btn3.setEnabled(False)


# 判斷網址輸入欄位是否有輸入資料， 並開啟Urls_Thread
def msg():
    global text
    ui.pushButton.setEnabled(False)
    text = ui.lineEdit.text()
    if text == "":
        QtWidgets.QMessageBox.about(MainWindow, "錯誤", "此欄位不能為空白")
        ui.pushButton.setEnabled(True)
    else:
        work.start()



# 開啟執行序，檢查所有影片是否都已經下載完成
class time_Thread(QtCore.QThread):
    stop_trigger = QtCore.pyqtSignal()
    trigger = QtCore.pyqtSignal()

    def __init__(self):
        super(time_Thread, self).__init__()
        self.trigger.connect(self.stop)
        self.timer = QtCore.QTimer()
        self.timer.moveToThread(self)
        self.timer.timeout.connect(self.ok)
        print("Ready")

    def run(self):
        self.timer.start(2000)
        self.exec_()

    def stop(self):
        self.quit()

    def ok(self):
        global check
        if False not in check:
            self.timer.stop()
            check = [False]
            self.stop_trigger.emit()
            self.trigger.emit()


# 開啟執行序並且判斷輸入資料是否為Youtube網址
class Urls_Thread(QtCore.QThread):
    trigger = QtCore.pyqtSignal()
    download_trigger = QtCore.pyqtSignal()

    def __init__(self):
        super(Urls_Thread, self).__init__()
        self.trigger.connect(self.get_urls)

    def run(self):
        self.trigger.emit()
        self.exec_()

    def get_urls(self):
        global urls, text

        try:
            YouTube(text)
        except:
            QtWidgets.QMessageBox.about(MainWindow, "錯誤", "下載器不支援此影片或網址錯誤")
            ui.pushButton.setEnabled(True)
            ui.lineEdit.clear()
            # print("已完成處理")
            self.quit()
            return

        # urls = URL.playlist_urls(text)
        urls = text
        self.download_trigger.emit()
        self.quit()


# 選填影片格式，儲存路徑 對話框
class InputdialogDemo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(InputdialogDemo, self).__init__(parent)
        layout = QtWidgets.QFormLayout()
        self.btn1 = QtWidgets.QPushButton("選擇下載格式")
        self.btn1.clicked.connect(self.getType)
        self.le1 = QtWidgets.QLineEdit()
        layout.addRow(self.btn1, self.le1)

        self.btn2 = QtWidgets.QPushButton("選擇影片畫質")
        self.btn2.clicked.connect(self.getRes)
        self.le2 = QtWidgets.QLineEdit()
        layout.addRow(self.btn2, self.le2)

        self.btn4 = QtWidgets.QPushButton("選擇儲存路徑")
        self.le4 = QtWidgets.QLineEdit()
        self.btn4.clicked.connect(self.save_Path)
        layout.addRow(self.btn4, self.le4)

        self.btn3 = QtWidgets.QPushButton("確定")
        self.btn3.clicked.connect(self.get)
        layout.addRow(self.btn3)

        self.btn2.setEnabled(False)
        self.le2.setEnabled(False)
        self.btn3.setEnabled(False)
        self.btn4.setEnabled(False)
        self.le4.setEnabled(False)

        self.setLayout(layout)
        self.setWindowTitle("選擇")

    def getType(self):

        global video_type, y
        self.btn4.setEnabled(False)
        self.le4.setEnabled(False)
        items = ["影片檔", "音源檔"]
        item, ok = QtWidgets.QInputDialog.getItem(self, "Select Type",
                                                  "Type：", items, 0, False)
        video_type = item
        print(video_type)
        print(ok)

        if ok and item == "影片檔" :
            self.btn3.setEnabled(False)
            self.le1.setText(item)
            self.btn2.setEnabled(True)
            self.le2.setEnabled(True)
            flag = False

        if ok and item == "音源檔" :
            self.btn2.setEnabled(False)
            self.le2.clear()
            self.le2.setEnabled(False)
            self.le1.setText(item)
            self.btn3.setEnabled(True)
            self.btn4.setEnabled(True)
            self.le4.setEnabled(True)
            flag = False



    def getRes(self):
        global select_video_quality, select
        items = select_video_quality
        item, ok = QtWidgets.QInputDialog.getItem(self, "Select Quality",
                                                  "Quality：", items, 0, False)
        select = item
        print(select)
        if ok and item:
            self.le2.setText(item)
            self.btn3.setEnabled(True)
            self.btn4.setEnabled(True)
            self.le4.setEnabled(True)

    def save_Path(self):
        global path
        item = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Path")
        path = item
        self.le4.setText(item)

    def get(self):
        threading.Thread(target=start_thread, args=(urls, 1)).start()
        self.close()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(140, 30, 541, 81))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 2, 1, 1, 1)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(140, 160, 541, 361))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.listWidget = QtWidgets.QListWidget(self.layoutWidget1)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout_2.addWidget(self.listWidget, 1, 0, 1, 1)
        # self.verticalScrollBar = QtWidgets.QScrollBar(self.layoutWidget1)
        # self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
        # self.verticalScrollBar.setObjectName("verticalScrollBar")
        # self.gridLayout_2.addWidget(self.verticalScrollBar, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Youtube極速下載器"))
        self.label.setText(_translate("MainWindow", "請輸入 YouTube 影片網址"))
        self.pushButton.setText(_translate("MainWindow", "下載影片"))
        self.label_2.setText(_translate("MainWindow", "下載狀態"))



if __name__ == "__main__":
    import sys


    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    # ----------------------------------------------------------
    ui.pushButton.clicked.connect(msg)
    ui.listWidget.setSortingEnabled(True)  # listWidget按照順序排序
    work = Urls_Thread()
    work.download_trigger.connect(ready_thread)
    trigger = time_Thread()
    trigger.stop_trigger.connect(finish_download)
    demo = InputdialogDemo()

    # -----------------------------------------------------------
    MainWindow.show()
    sys.exit(app.exec_())



# 增加選擇下載路徑，影片格式(清單式)，優化GUI
# URL.py requests_html無法打包 ， 會出現錯誤
