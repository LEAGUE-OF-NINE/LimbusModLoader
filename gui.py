import logging
import sys

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QProgressBar, \
    QMessageBox

from compress import compress_lunartique_mod

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)


class FileCompressThread(QThread):
    end_of_run = pyqtSignal()
    error_at_run = pyqtSignal(Exception)
    progress_update = pyqtSignal(int)

    def __init__(self, input_file_path, output_file_path):
        super().__init__()
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def run(self):
        try:
            logging.info("Compressing lunartique format mod (might take a while!): %s", self.input_file_path)
            compress_lunartique_mod(self.input_file_path, self.output_file_path,
                                    update_progress=self.progress_update.emit)
            self.end_of_run.emit()
        except Exception as e:
            self.error_at_run.emit(e)


class FileCompressor(QWidget):
    def __init__(self):
        super().__init__()

        self.worker_thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Limbus Mod Compressor')

        layout = QVBoxLayout()

        self.input_file_label = QLabel('Input File (Lunartique format mod):')
        layout.addWidget(self.input_file_label)

        self.input_file_button = QPushButton('Select File', self)
        self.input_file_button.clicked.connect(self.select_input_file)
        layout.addWidget(self.input_file_button)

        self.output_file_label = QLabel('Output Location:')
        layout.addWidget(self.output_file_label)

        self.output_file_button = QPushButton('Select Location', self)
        self.output_file_button.clicked.connect(self.select_output_location)
        layout.addWidget(self.output_file_button)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.compress_button = QPushButton('Compress', self)
        self.compress_button.clicked.connect(self.compress_file)
        layout.addWidget(self.compress_button)

        self.setLayout(layout)

        self.input_file_path = ''
        self.output_file_path = ''

    def select_input_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'Zip Files (*.zip)', options=options)
        if fileName:
            self.input_file_path = fileName
            self.input_file_label.setText('Input File: ' + fileName)

    def select_output_location(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        fileName, _ = QFileDialog.getSaveFileName(self, 'Select Location', '', 'Carra mods (*.carra)', options=options)
        if fileName:
            if not fileName.endswith(".carra"):
                fileName += ".carra"
            self.output_file_path = fileName
            self.output_file_label.setText('Output Location: ' + fileName)

    def compress_file(self):
        if not self.input_file_path or not self.output_file_path:
            QMessageBox.warning(self, 'Error', 'Please select both input file and output location.')
            return

        self.compress_button.setEnabled(False)
        self.update_progress(0)
        self.worker_thread = FileCompressThread(self.input_file_path, self.output_file_path)
        self.worker_thread.progress_update.connect(self.update_progress)
        self.worker_thread.end_of_run.connect(lambda: self.compress_file_finished(None))
        self.worker_thread.error_at_run.connect(self.compress_file_finished)
        self.worker_thread.start()

    def compress_file_finished(self, exception):
        if exception:
            QMessageBox.critical(self, 'Error', f'An error occurred: {exception}')
        else:
            QMessageBox.information(self, 'Success', 'File compressed successfully!')
        self.compress_button.setEnabled(True)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()


def __main__():
    app = QApplication(sys.argv)
    ex = FileCompressor()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    __main__()
