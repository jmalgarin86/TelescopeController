import datetime
import time

import cv2
import numpy as np

from widgets.widget_tasks import TasksWidget
import imreg_dft as ird


class TasksController(TasksWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.roi_points = None

        self.button_align.clicked.connect(self.alignImages)
        self.button_dark.clicked.connect(self.removeDark)
        self.button_noise.clicked.connect(self.sortByNoise)
        self.button_fwhm.clicked.connect(self.sortByFwhm)
        self.button_select.clicked.connect(self.selectSlices)
        self.button_average.clicked.connect(self.averageFrames)
        self.button_background.clicked.connect(self.subtractBackground)
        self.button_sharp.clicked.connect(self.fixAberration)

    def fixAberration(self):
        # Get image
        frame = self.main.frames * 1
        frame = (frame / np.max(frame[:]) * 255.0).astype(np.uint8)

        # Get individual channels
        red_channel = frame[:, :, 0]
        green_channel = frame[:, :, 1]
        blue_channel = frame[:, :, 2]

        # Select reference channel
        reference_channel = red_channel

        # Perform color channel alignment (registration)
        # Using imreg's translation-based registration
        translation = ird.translation(blue_channel, reference_channel)
        aligned_blue_channel = ird.transform_img(blue_channel, translation)

        translation = ird.translation(green_channel, reference_channel)
        aligned_green_channel = ird.transform_img(green_channel, translation)

        frame[:, :, 0] = red_channel
        frame[:, :, 1] = aligned_green_channel
        frame[:, :, 2] = aligned_blue_channel

        self.main.frame = frame * 1

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result

        return 0

    def subtractBackground(self):
        # Get frames
        frames = self.main.frames
        frames_grayscale = self.main.frames_grayscale
        x = []
        y = []

        # Get roi
        idx = self.main.roi_points
        try:
            roi_data = frames[idx[0]:idx[1], idx[2]:idx[3], :]
        except:
            print("Frames should be 2D for background subtraction")
            return

        # Get background for each channel
        b0 = np.average(frames[:, :, 0], axis=(0, 1))
        b1 = np.average(frames[:, :, 1], axis=(0, 1))
        b2 = np.average(frames[:, :, 2], axis=(0, 1))

        # Do subtraction
        frames[:, :, 0] -= b0
        frames[:, :, 1] -= b1
        frames[:, :, 2] -= b2

        self.main.frames = np.abs(frames)
        self.main.frames_grayscale = np.average(frames, axis=2)

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result

        return 0

    def removeDark(self):
        frames_rgb = np.zeros_like(self.main.frames)
        dark = self.main.frame_dark * 1
        dark = (dark / np.max(dark[:]) * 255.0).astype(np.uint8)

        for ii in range(np.size(frames_rgb, 0)):
            frames_rgb[ii, :, :, :] = self.main.frames[ii, :, :, :] - dark
        self.main.frames = np.abs(frames_rgb)

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result

    @staticmethod
    def get_fwhm(data):
        # Calculate fwhm for axis 0
        proj = np.sum(data, axis=0)
        idx = np.argmax(proj)
        proj_tar = proj[idx] / 2
        proj_a = np.abs(proj[0:idx] - proj_tar)
        idx_a = np.argmin(proj_a)
        proj_b = np.abs(proj[idx::] - proj_tar)
        idx_b = idx + np.argmin(proj_b)
        fwhm_x = idx_b - idx_a

        proj = np.sum(data, axis=1)
        idx = np.argmax(proj)
        proj_tar = proj[idx] / 2
        proj_a = np.abs(proj[0:idx] - proj_tar)
        idx_a = np.argmin(proj_a)
        proj_b = np.abs(proj[idx::] - proj_tar)
        idx_b = idx + np.argmin(proj_b)
        fwhm_y = idx_b - idx_a

        return fwhm_x, fwhm_y

    def sortByFwhm(self):
        # Get images
        frames_rgb = self.main.frames
        frames_gra = self.main.frames_grayscale

        # Get roi
        idx = self.main.roi_points
        try:
            roi_data = frames_gra[:, idx[0]:idx[1], idx[2]:idx[3]]
        except:
            print("Frames should be 3D")
            return

        fwhm_x = []
        fwhm_y = []
        for f in range(np.size(frames_gra, 0)):
            fwhm_x0, fwhm_y0 = self.get_fwhm(roi_data[f])
            fwhm_x.append(fwhm_x0)
            fwhm_y.append(fwhm_y0)

        fwhm_x = np.array(fwhm_x)
        fwhm_y = np.array(fwhm_y)
        fwhm = np.concatenate((fwhm_x, fwhm_y), axis=0)
        fwhm = np.reshape(fwhm, (2, -1))
        fwhm = np.max(fwhm, axis=0)
        ind = np.argsort(fwhm)
        self.main.frames = self.main.frames[ind]
        self.main.frames_grayscale = self.main.frames_grayscale[ind]
        fwhm = fwhm[ind]
        fwhm_x = fwhm_x[ind]
        fwhm_y = fwhm_y[ind]
        x = np.linspace(1, np.size(roi_data, 0), np.size(roi_data, 0))

        # Create resulting dictionary
        result1 = {
            'kind': 'curve',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
            'x_data': x,
            'y_data': [fwhm_x, fwhm_y],
            'legend': ['y', 'x'],
        }

        result2 = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Save items
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result1

        time.sleep(0.01)
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result2

    def averageFrames(self):
        self.main.frames = np.average(self.main.frames, 0)
        self.main.frames_grayscale = np.average(self.main.frames_grayscale, 0)

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result

        # Convert image_rgb to uint8
        image_rgb = (self.main.frames / np.max(self.main.frames[:]) * 255.0).astype(np.uint8)

        # Reorganize
        image_rgb = image_rgb[:, :, ::-1]
        image_rgb = np.transpose(image_rgb, [1, 0, 2])

        cv2.imwrite(filename='results/result.png', img=image_rgb)

    def selectSlices(self):
        text = self.text.text()
        idx = text.split(" ")
        i0 = int(idx[0])
        i1 = int(idx[1])
        self.main.frames = self.main.frames[i0:i1]
        self.main.frames_grayscale = self.main.frames_grayscale[i0:i1]

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result

    def sortByNoise(self):
        # Get roi
        frames_grayscale = self.main.frames_grayscale
        idx = self.main.roi_points
        try:
            roi_data = frames_grayscale[:, idx[0]:idx[1], idx[2]:idx[3]]
        except:
            print("Frames should be 3D to be aligned")
            return

        # Get mean value of the roi
        noise = np.average(roi_data, axis=(1, 2))
        ind = np.argsort(noise)
        self.main.frames = self.main.frames[ind]
        self.main.frames_grayscale = self.main.frames_grayscale[ind]
        noise = noise[ind]
        x = np.linspace(1, np.size(roi_data, 0), np.size(roi_data, 0))

        # Create resulting dictionary
        result1 = {
            'kind': 'curve',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
            'x_data': x,
            'y_data': [noise],
            'legend': [''],
        }

        result2 = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Save items
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result1

        time.sleep(0.01)
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result2


    def alignImages(self):
        # Get frames
        frames = self.main.frames
        frames_grayscale = self.main.frames_grayscale
        x = []
        y = []

        # Get roi
        idx = self.main.roi_points
        try:
            roi_data = frames_grayscale[:, idx[0]:idx[1], idx[2]:idx[3]]
        except:
            print("Frames should be 3D to be aligned")
            return

        # Match roi with frames to find the image displacement
        for frame_grayscale in frames_grayscale:
            result = cv2.matchTemplate(frame_grayscale, roi_data[self.main.roi_ind], cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            x0, y0 = max_loc
            x.append(x0)
            y.append(y0)
        x = np.array(x)
        dx = x - x[0]
        y = np.array(y)
        dy = y - y[0]

        # Get the dimensions (width and height) of image2
        _, height, width = frames_grayscale.shape

        # Create an empty image of the same size as image2
        frames0_grayscale = np.zeros_like(frames_grayscale)
        frames0 = np.zeros_like(frames)

        # Align all the frames
        x1_lim = 0
        x2_lim = width
        y1_lim = 0
        y2_lim = height
        for ii in range(np.size(frames, 0)):
            # Calculate the new coordinates for image2 after shifting
            x1 = max(0, dx[ii])  # Ensure x1 is not negative
            x2 = min(width + dx[ii], width)  # Ensure x2 does not exceed the width
            y1 = max(0, dy[ii])  # Ensure y1 is not negative
            y2 = min(height + dy[ii], height)  # Ensure y2 does not exceed the height

            # Calculate the region in image1 where image2 will be placed
            x1_dst = max(0, -dx[ii])  # Destination coordinates
            x2_dst = min(width, width - dx[ii])
            y1_dst = max(0, -dy[ii])
            y2_dst = min(height, height - dy[ii])

            # Check for boundaries
            if x1_dst > x1_lim:
                x1_lim = x1_dst
            if x2_dst < x2_lim:
                x2_lim = x2_dst
            if y1_dst > y1_lim:
                y1_lim = y1_dst
            if y2_dst < y2_lim:
                y2_lim = y2_dst

            # Copy the shifted region from image2 to the corresponding region in shifted_image2
            frames0[ii, y1_dst:y2_dst, x1_dst:x2_dst] = frames[ii, y1:y2, x1:x2, :]
            frames0_grayscale[ii, y1_dst:y2_dst, x1_dst:x2_dst] = frames_grayscale[ii, y1:y2, x1:x2]

        self.main.frames = frames0[:, y1_lim:y2_lim, x1_lim:x2_lim, :]
        self.main.frames_grayscale = frames0_grayscale[:, y1_lim:y2_lim, x1_lim:x2_lim]

        # Create resulting dictionary
        result = {
            'kind': 'image',
            'data_rgb': self.main.frames * 1,
            'data_gra': self.main.frames_grayscale * 1,
        }

        # Get the current time
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.main.history_controller.addItem(time_string)
        self.main.history_controller.history_dictionary[time_string] = result

        return 0
