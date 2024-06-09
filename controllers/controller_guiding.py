from widgets.widget_guiding import GuidingWidget


class GuidingController(GuidingWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.reference_button.clicked.connect(self.set_reference)
        self.set_threshold_button.clicked.connect(self.set_threshold)
        self.checkbox_astrophoto.clicked.connect(self.set_astrophoto_mode)

    def set_astrophoto_mode(self):
        if self.checkbox_astrophoto.isChecked():
            print("Astro photo mode activated")
            self.main.guide_camera_controller.set_astrophoto_mode(True)
        else:
            print("Astro photo mode deactivated")
            self.main.guide_camera_controller.set_astrophoto_mode(False)

    def set_reference(self):
        # Get values in the text
        text = self.pixel_edit.text()
        if text == '':
            text = self.pixel_edit.placeholderText()
        pixel = tuple(map(int, text.split(',')))

        self.main.guide_camera_controller.set_looseness(0)
        self.main.guide_camera_controller.set_reference_position(pixel)
        print("Reference position: x, y: %0.0f, %0.0f" % (pixel[0], pixel[1]))

    def set_threshold(self):
        text = self.threshold_edit.text()
        if text == '':
            text = self.threshold_edit.placeholderText()
        threshold = int(text)

        self.main.guide_camera_controller.set_star_threshold(threshold)
        print("Star size threshold: %0.0f" % threshold)



