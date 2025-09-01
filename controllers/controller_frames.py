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
        self._old_file = None
        self._sniffer_running = False
        self.main = main
        self._camera = camera
        self.path = f"captures/captures_{self._camera}"

        # Create folder to search frames
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(100)

        thread = threading.Thread(target=self._run_frame_sniffer)
        thread.start()

        print(f'{camera} sniffer started')

    def _update_frame(self):
        if self._n_frames_old < self._n_frames:
            self._n_frames_old = self._n_frames
            if self._camera == 'guide':
                print("Frame in guide")
                self.main.image_guide_camera.on_guide_frame_ready(self._frame)
            elif self._camera == 'main':
                print("Frame in main")
                self.main.image_main_camera.on_main_frame_ready(self._frame)

    def _run_frame_sniffer(self):
        while self.main.gui_open:
            file = utils.get_last_file_in_directory(self.path)
            if file != self._old_file:
                self._old_file = file
                self._n_frames += 1
                self._frame = utils.extract_image_matrix(f"captures/captures_{self._camera}/{file}")
            time.sleep(0.1)

if __name__ == "__main__":
    frame_sniffer = FrameSniffer()