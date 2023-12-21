import copy
import os
import threading
import time

from widgets.widget_multipicture import MultipictureWidget


class MultipictureController(MultipictureWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.startButton.clicked.connect(self.checkIfSweep)

    def checkIfSweep(self):
        if self.startButton.isChecked():
            print("\nStart multi-picture")
            thread = threading.Thread(target=self.multiPicture2)
            thread.start()
        else:
            print("\nStop multi-picture")

    def multiPicture2(self):

        # Get number
        matrix_size = self.matrixSizeLineEdit.text()
        n = [int(x) for x in matrix_size.split(',')]

        # Get displacement
        steps_str = self.stepMovementLineEdit.text()
        steps = [str(int(x)) for x in steps_str.split(',')]

        # Move the mount to the first frame
        n_ar = str(int(int(steps[0]) * (n[0] / 2 - 0.5)))
        n_de = str(int(int(steps[1]) * (n[1] / 2 - 0.5)))
        command = "0 " + n_ar + "1 2 " + n_de + "1 2"
        self.main.waiting_commands.append(command)

        # Get number of frames until next region
        n_frames = int(self.framesLineEdit.text())

        # Get initial directory
        initial_files = os.listdir("sharpcap")

        for ii in range(n[1]):
            for jj in range(n[0]):
                new_folder = False
                while not new_folder:
                    current_files = os.listdir("sharpcap")
                    if len(current_files) == len(initial_files):
                        time.sleep(0.1)
                    else:
                        # Get the new folder and create the path to the new folder
                        new_folders = [folder for folder in current_files if
                                       folder not in initial_files and os.path.isdir(os.path.join("sharpcap", folder))]
                        new_folder = new_folders[0]
                        folder_path = os.path.join("sharpcap", new_folder)
                        print("Start sequence %i, %i" % (jj+1, ii+1))

                        # Update initial_files
                        initial_files = copy.copy(current_files)

                        # Wait until number of frames is reached to move the mount
                        finish = False
                        while not finish:
                            n_files = len(os.listdir(folder_path)) - 1
                            if n_files >= n_frames:
                                finish = True
                                command = "0 0 0 52 0 0 0\n"

                                # Move frame position:
                                if jj < n[0] - 1 and ii % 2 == 0:
                                    ar_command = " " + steps[0] + " 0 2"
                                    de_command = " 0 0 0"
                                    command = "0" + ar_command + de_command + "\n"
                                elif jj < n[0] - 1 and ii % 2 == 1:
                                    ar_command = " " + steps[0] + " 1 2"
                                    de_command = " 0 0 0"
                                    command = "0" + ar_command + de_command + "\n"
                                elif jj == n[0] - 1:
                                    ar_command = " 0 0 52"
                                    de_command = " " + steps[1] + " 0 2"
                                    command = "0" + ar_command + de_command + "\n"

                                # Send command to arduino
                                if ii == n[1] - 1 and jj == n[0] - 1:
                                    print("\nReady!")
                                    self.startButton.setChecked(False)
                                else:
                                    self.main.waiting_commands.append(command)
