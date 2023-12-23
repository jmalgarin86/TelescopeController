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
        command = "0 " + n_ar + " 1 2 " + n_de + " 1 2"
        self.main.waiting_commands.append(command)
        print(command)

        # Get number of frames until next region
        n_frames = int(self.framesLineEdit.text())

        # Get initial directory
        items = os.listdir("sharpcap")
        initial_folders = [item for item in items if os.path.isdir(os.path.join("sharpcap",item))]

        for ii in range(n[1]):
            for jj in range(n[0]):
                new_folder = False
                while not new_folder and self.startButton.isChecked():
                    items = os.listdir("sharpcap")
                    current_folders = [item for item in items if os.path.isdir(os.path.join("sharpcap",item))]
                    if len(current_folders) > len(initial_folders):
                        # Print info of new sequence
                        print("Start sequence %i, %i" % (jj + 1, ii + 1))

                        # Get the new folder and create the path to the new folder
                        new_folders = [folder for folder in current_folders if
                                       folder not in initial_folders and os.path.isdir(os.path.join("sharpcap", folder))]
                        try:
                            new_folder = new_folders[0]
                        except:
                            print("Fatal error, no new folder found")
                            print(initial_folders)
                            print(current_folders)
                            return
                        folder_path = os.path.join("sharpcap", new_folder)

                        # Update initial_files
                        initial_folders = current_folders

                        # Wait until number of frames is reached to move the mount
                        finish = False
                        n_files_0 = 0
                        while not finish and self.startButton.isChecked():
                            # Get number of files into the current folder
                            n_files_1 = len(os.listdir(folder_path)) - 1

                            # Print info if a new file is found
                            if n_files_1 > n_files_0:
                                n_files_0 = n_files_1
                                print("Frames: %i" % n_files_1)

                            # Move to next frame if n_files equals to desired n_frames
                            if n_files_1 >= n_frames:
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
                                    print("Progress: %i %%" % (int((ii+1)*(jj+1)/(n[0]*n[1])*100)))
                                    print("Moving to next sequence")
                                    print(command)
                            time.sleep(0.1)
                    time.sleep(0.1)
