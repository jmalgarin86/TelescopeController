"""
:author:    J.M. Algarín
:email:     josalggui@i3m.upv.es
:affiliation: MRILab, i3M, CSIC, Valencia, Spain

"""

import sys
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from widgets.widget_console import ConsoleWidget
import datetime


class ConsoleController(ConsoleWidget):
    """
    Console controller class.

    This class extends the `ConsoleWidget` class and serves as a controller for the console functionality. It redirects
    the output of print statements to the console widget.

    Methods:
        __init__(): Initialize the ConsoleController instance.
        write_console(text): Write text to the console widget.

    Signals:
        None
    """

    def __init__(self):
        super().__init__()

        # Redirect the output of print to the console widget and log it
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = f"log_files/log_{current_datetime}.txt"
        self.emitting_stream = EmittingStream(log_file_path=log_file_path)
        sys.stdout = self.emitting_stream

        # Connect the signal to the write_console method
        self.emitting_stream.textWritten.connect(self.write_console)

    def write_console(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

class EmittingStream(QObject):
    """
    Emitting stream class.

    This class emits a signal with the text written and provides a write method to redirect the output.

    Methods:
        write(text): Write text and emit the signal.
        flush(): Placeholder method for flushing the stream.

    Signals:
        textWritten (str): A signal emitted with the text written.
    """

    textWritten = pyqtSignal(str)

    def __init__(self, log_file_path=None):
        super().__init__()
        self.log_file_path = log_file_path
        if self.log_file_path:
            self.log_file = open(self.log_file_path, 'a')  # Open the log file in append mode

    def write(self, text):
        # Get the current date and time
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        # Prepend the time to the text
        if text == "\n" or text == " ":
            formatted_text = text
        else:
            formatted_text = f"{current_time} - {text}"

        # Write to the log file if a path is provided
        if self.log_file_path:
            self.log_file.write(formatted_text)
            self.log_file.flush()  # Ensure the text is written immediately

        # Emit the signal with the timestamped text
        self.textWritten.emit(str(formatted_text))

    @pyqtSlot()
    def flush(self):
        if self.log_file_path:
            self.log_file.flush()

    def close(self):
        if self.log_file_path:
            self.log_file.close()