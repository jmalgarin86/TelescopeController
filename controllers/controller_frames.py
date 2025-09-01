import os
import shutil
import threading
import time

from PyQt5.QtCore import QTimer

from utils import utils


class FrameSniffer:
    def __init__(self, main=None, camera='guiding'):
        super().__init__()
        self._n_frames_total = 0
        self._saving_path = "captures/"
        self._n_frames_to_save = 0
        self._n_frames = 0
        self._n_frames_old = 0
        self._frame = None
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
            if self._camera == 'guide' and self._frame is not None:
                self.main.image_guide_camera.on_guide_frame_ready(self._frame)
            if self._camera == 'main' and self._frame is not None:
                self.main.image_main_camera.on_main_frame_ready(self._frame)

    def _run_frame_sniffer(self):
        while self.main.gui_open:
            path = utils.get_last_folder_in_directory(self.path)
            utils.delete_all_except_last(path)
            file_path = f"{path}/{utils.get_last_file_in_directory(path)}"
            if file_path != self._old_file and path is not None:
                self._old_file = file_path
                self._n_frames += 1
                self._frame = utils.extract_image_matrix(file_path)
                if self._n_frames_to_save > 0:
                    self._n_frames_to_save -= 1
                    print(f"{self._n_frames_total - self._n_frames_to_save}/{self._n_frames_total}, {file_path}")
                    thread = threading.Thread(target=self._copy_file)
                    thread.start()
            time.sleep(0.1)

    def set_frames_to_save(self, n=0, path='captures/'):
        self._n_frames_to_save = n
        self._n_frames_total = n
        self._saving_path = path

    def _copy_file(self):
        try:
            if not os.path.isfile(self._old_file):
                return f"Source file not found: {self._old_file}"

            # Copy file to destination
            shutil.copy2(self._old_file, self._saving_path)

            return f"File copied to {self._saving_path}"

        except PermissionError:
            return "Permission denied"
        except Exception as e:
            return str(e)


if __name__ == "__main__":
    frame_sniffer = FrameSniffer()