import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QScrollArea

# from demo3 import QTimeLine
from TimelineWidget import TimelineWidget
from main import Ui_MainWindow
from playvideo import StreamVideo


class MainWindowActivity(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindowActivity, self).__init__()
        self.setupUi(self)
        # self.showMaximized()

        layoutBody = QVBoxLayout(self.frame_time_line)
        layoutBody.setContentsMargins(0, 0, 0, 0)
        self.frame_time_line.setLayout(layoutBody)

        self.time_ranges_seconds = []
        pathFoder = "video"
        listFile = os.listdir(pathFoder)
        for file in listFile:
            numberS = file.replace(".mkv", "")
            array = numberS.split("_")
            timeFiles = array[0].split(":")
            s = int(timeFiles[0]) * 3600 + int(timeFiles[1]) * 60 + int(timeFiles[2])
            self.time_ranges_seconds.append((s, s + 600, file))

        self.listNameSort = self.sort_listFile()

        timeline = TimelineWidget(self.time_ranges_seconds)
        timeline.timelineSignal.connect(self.update_position)
        timeline.setMinimumSize(20000, 50)  # Đặt kích thước tối thiểu để cuộn ngang
        scroll_area = QScrollArea(self.frame_time_line)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(timeline)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layoutBody.addWidget(scroll_area)

        self.streamVideo = StreamVideo(self.listNameSort)
        self.streamVideo.imageSignal.connect(self.update_frame)
        self.streamVideo.stopSignal.connect(self.stop_video)
        self.streamVideo.start()

    def update_position(self, position):

        timeFiles = position.split(":")
        s = int(timeFiles[0]) * 3600 + int(timeFiles[1]) * 60 + int(timeFiles[2])
        check = False
        # check s in time_ranges_seconds
        for item in self.time_ranges_seconds:
            if s >= item[0] and s <= item[1]:
                # print("seek to: {}".format(item[2]))
                check = True
                seek = s - item[0]
                # print("seek: {}".format(seek))
                if not self.streamVideo.IS_RUNNING_NEXT:
                    print("start new video")
                    self.streamVideo = StreamVideo(self.listNameSort, self.listNameSort.index(item[2]), True, seek)
                    self.streamVideo.imageSignal.connect(self.update_frame)
                    self.streamVideo.stopSignal.connect(self.stop_video)
                    self.streamVideo.start()
                else:
                    print("seek to: {}".format(item[2]))
                    self.streamVideo.seekTo(seek, item[2])
                break
        if not check:
            self.streamVideo.stop()

        # self.streamVideo.seekTo(position * self.content.getScale())

    def stop_video(self):
        # clear frame
        self.label.clear()
        self.label.setText("Video is stopped")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: red; font-size: 20px; font-weight: bold")



    def update_frame(self, frame):
        import cv2
        frame = cv2.resize(frame, (1280, 720))
        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Tạo QPixmap trực tiếp từ frame BGR
        pixmap = QPixmap.fromImage(
            QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888))

        # Hiển thị QPixmap trên QLabel
        self.label.setPixmap(pixmap)

    def sort_listFile(self):
        listNumber = []
        for item1, item2, item3 in self.time_ranges_seconds:
            listNumber.append(item1)
        listNumber.sort()
        listFileChange = []
        for number in listNumber:
            for item1, item2, item3 in self.time_ranges_seconds:
                if number == item1:
                    listFileChange.append(item3)

        return listFileChange


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindowActivity()
    window.show()
    sys.exit(app.exec_())
