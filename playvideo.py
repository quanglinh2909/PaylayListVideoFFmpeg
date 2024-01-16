

import logging
import time

from PyQt5.QtCore import QThread, pyqtSignal, Qt
import ffmpeg
import numpy as np



class StreamVideo(QThread):
    imageSignal = pyqtSignal(object)
    startSignal = pyqtSignal()
    stopSignal = pyqtSignal()
    errorSignal = pyqtSignal(str)

    def __init__(self,source,index=0,isSeek=False,seek=0):
        super(StreamVideo, self).__init__()
        self.source = source
        self.isSeek = isSeek
        self.seek = seek
        self.IS_RUNNING_VIDEO = True
        self.IS_RUNNING_NEXT = True
        self.index = index
        self.current_source = None


    def run(self):
        while self.IS_RUNNING_NEXT:
            args = {}
            if self.index >= len(self.source):
                break
            self.current_source = "video/" + self.source[self.index]
            self.index += 1
            probe = ffmpeg.probe(self.current_source)
            cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
            print("fps: {}".format(cap_info['r_frame_rate']))
            width = cap_info['width']
            height = cap_info['height']
            up, down = str(cap_info['r_frame_rate']).split('/')
            fps = eval(up) / eval(down)
            print("fps: {}".format(fps))
            # print("duration: {}".format(cap_info['duration']))
            if self.isSeek:
                self.isSeek = False
                process1 = (
                    ffmpeg
                    .input(self.current_source, ss=self.seek, **args)
                    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                    .overwrite_output()
                    .run_async(pipe_stdout=True)
                )
            else:
                process1 = (
                    ffmpeg
                    .input(self.current_source, **args)
                    .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                    .overwrite_output()
                    .run_async(pipe_stdout=True)
                )
            self.IS_RUNNING_VIDEO = True

            while self.IS_RUNNING_VIDEO:
                start_time = time.time()  # Ghi lại thời gian bắt đầu xử lý frame
                if self.isSeek:
                    self.isSeek = False
                    # Seek back to the 1st second
                    process1 = (
                        ffmpeg
                        .input(self.current_source, ss=self.seek, **args)
                        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                        .overwrite_output()
                        .run_async(pipe_stdout=True)
                    )
                    start_time = time.time()
                in_bytes = process1.stdout.read(width * height * 3)
                if not in_bytes:
                    break
                in_frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
                self.imageSignal.emit(in_frame)
                # Tính thời gian còn lại trước khi hiển thị khung hình tiếp theo
                elapsed_time = time.time() - start_time
                time_to_sleep = max(0, 1 / fps - elapsed_time)
                time.sleep(time_to_sleep)


            process1.kill()

    def seekTo(self, seek,source=None):
        if self.current_source == source:
            self.isSeek = True
            self.seek = seek
        else:
            self.IS_RUNNING_VIDEO = False
            self.isSeek = True
            self.seek = seek
            self.current_source = source
            self.index = self.source.index(source)

    def stop(self):
        self.IS_RUNNING_NEXT = False
        self.IS_RUNNING_VIDEO = False
        self.stopSignal.emit()
        self.terminate()




