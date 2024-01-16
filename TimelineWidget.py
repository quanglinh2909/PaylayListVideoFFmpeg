import sys
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, pyqtSignal


class TimelineWidget(QWidget):
    timelineSignal = pyqtSignal(object)

    def __init__(self, time_ranges=[]):
        super().__init__()
        self.time_ranges = time_ranges
        self.selected_time = None

    def minimumSizeHint(self):
        return self.sizeHint()

    def sizeHint(self):
        return self.minimumSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_timeline(painter)

    def draw_timeline(self, painter):
        # Thiết lập màu nền
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(0, 0, self.width(), self.height())

        # Thiết lập màu và kiểu nét vẽ
        pen = QPen()
        pen.setColor(QColor(0, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)

        # Vẽ timeline
        hour_width = self.width() / 24
        for i in range(24):
            x = int(i * hour_width)
            painter.drawLine(x, 30, x, 70)  # Đường kẻ dọc
            painter.drawText(x, 20, f'{i}:00')  # Chữ số giờ

            # Vẽ các dòng và chữ số phút
            for minute in range(1, 60):
                x_minute = int(x + (hour_width / 60) * minute)
                painter.drawLine(x_minute, 40, x_minute, 60)  # Đường kẻ dọc cho phút

        # Vẽ đoạn thời gian có màu xanh lá cây
        painter.setBrush(QColor(0, 255, 0, 100))  # Màu xanh lá cây với độ trong suốt
        for start_seconds, end_seconds,_ in self.time_ranges:
            start_x = int(start_seconds / 3600 * hour_width)
            end_x = int(end_seconds / 3600 * hour_width)
            painter.drawRect(start_x, 0, end_x - start_x, self.height())

        # Vẽ đường thời gian được chọn màu đỏ
        if self.selected_time:
            selected_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(self.selected_time.split(':'))))
            selected_x = int(selected_seconds / 3600 * hour_width)
            pen.setColor(QColor(255, 0, 0))
            painter.setPen(pen)
            painter.drawLine(selected_x, 0, selected_x, self.height())

    def mousePressEvent(self, event):
        # Xác định vị trí chuột khi click
        pos = event.pos()

        # Tính toán giờ, phút và giây từ vị trí chuột
        hour_width = self.width() / 24
        total_seconds = int(pos.x() / hour_width * 3600)  # Chuyển đổi thành số nguyên
        clicked_hour = total_seconds // 3600
        clicked_minute = (total_seconds % 3600) // 60
        clicked_second = total_seconds % 60

        # Lưu trữ thời gian được chọn
        self.selected_time = f'{clicked_hour:02d}:{clicked_minute:02d}:{clicked_second:02d}'

        # In thông tin về giờ, phút và giây khi click chuột
        # print(f'Selected Time: {self.selected_time}')
        self.timelineSignal.emit(self.selected_time)

        # Vẽ lại timeline để làm nổi bật thời gian được chọn
        self.update()

    # def wheelEvent(self, event):
    #     # Xử lý sự kiện cuộn chuột để cuộn ngang
    #     delta = event.angleDelta().y()
    #
    #     self.scroll(int(-delta / 8), 0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setGeometry(100, 100, 1000, 100)

    scroll_area = QScrollArea(window)
    scroll_area.setGeometry(0, 0, 1000, 100)

    # Danh sách đoạn thời gian (ví dụ: 3 giờ đến 6 giờ và 8 giờ đến 12 giờ)
    time_ranges_seconds = [(1 * 3600 + 30, 2 * 3600), (8 * 3600, 12 * 3600)]
    timeline = TimelineWidget(time_ranges_seconds)
    timeline.setMinimumSize(20000, 50)  # Đặt kích thước tối thiểu để cuộn ngang
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(timeline)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    window.show()
    sys.exit(app.exec_())
