import os
import threading
import time

from PyQt5.QtCore import QTimer

from utils import utils


class FrameSniffer:
    def __init__(self, main=None, camera='guiding'):
        super().__init__()
        self._n_frames = 0
        self._n_frames_old = 0
        self._sniffer_running = False
        self.main = main
        self.camera = camera
        self.path = f"captures/captures_{self.camera}"

        # Create folder to search frames
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)

        thread = threading.Thread(target=self._run_frame_sniffer)
        thread.start()

    def set_status(self, status: bool):
        self._sniffer_running = status
        if status:
            self.timer.start(1000)
        else:
            self.timer.stop()

    def _update_frame(self):
        if self._n_frames_old < self._n_frames:
            self._n_frames_old = self._n_frames
            if self.camera == 'guiding':
                self.main.image_guide_camera.on_guide_frame_ready(self._frame)
            elif self.camera == 'main':
                self.main.image_main_camera.on_main_frame_ready(self._frame)

    def _run_frame_sniffer(self):
        while self.main.gui_open:
            while self._sniffer_running:
                file = utils.get_last_file_in_directory(self.path)
                self._frame = utils.extract_image_matrix(file)
                time.sleep(0.1)
            time.sleep(0.1)

if __name__ == "__main__":
    frame_sniffer = FrameSniffer()