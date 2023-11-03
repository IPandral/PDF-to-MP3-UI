import sys
import os
import subprocess
import pyttsx3
from PyPDF2 import PdfReader
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QMessageBox
)
from threading import Thread

class PDFtoMP3Converter(QMainWindow):
    conversion_complete_signal = pyqtSignal(str)  # Signal to indicate conversion is complete

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF to MP3")
        self.setGeometry(100, 100, 280, 170)

        layout = QVBoxLayout()

        self.title_label = QLabel("PDF to MP3", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.pdf_path_label = QLabel("Select a PDF file", self)
        layout.addWidget(self.pdf_path_label)

        self.select_pdf_button = QPushButton("Select PDF", self)
        self.select_pdf_button.clicked.connect(self.select_pdf)
        layout.addWidget(self.select_pdf_button)

        self.output_path_label = QLabel("Select output folder", self)
        layout.addWidget(self.output_path_label)

        self.select_output_button = QPushButton("Select Output", self)
        self.select_output_button.clicked.connect(self.select_output)
        layout.addWidget(self.select_output_button)

        self.convert_button = QPushButton("Convert", self)
        self.convert_button.clicked.connect(self.convert)
        layout.addWidget(self.convert_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.pdf_file_path = None
        self.output_dir_path = None

        self.conversion_complete_signal.connect(self.on_conversion_complete)

    def select_pdf(self):
        pdf_file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF files (*.pdf)")
        if pdf_file:
            self.pdf_path_label.setText(pdf_file)
            self.pdf_file_path = pdf_file

    def select_output(self):
        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_path:
            self.output_path_label.setText(output_path)
            self.output_dir_path = output_path

    def convert(self):
        if self.pdf_file_path and self.output_dir_path:
            self.convert_button.setEnabled(False)  # Disable the button while processing
            # Run the conversion in a separate thread to avoid freezing the UI
            conversion_thread = Thread(target=self.convert_pdf_to_mp3, args=(self.pdf_file_path, self.output_dir_path))
            conversion_thread.start()
        else:
            QMessageBox.warning(self, "Warning", "Please select both a PDF file and output directory.")

    def convert_pdf_to_mp3(self, pdf_path, output_dir):
        try:
            speaker = pyttsx3.init()
            pdf_file = os.path.basename(pdf_path)
            pdf_file_name = os.path.splitext(pdf_file)[0]  # Get the file name without the extension

            # Create a subfolder within the output directory named after the PDF file
            pdf_output_dir = os.path.join(output_dir, pdf_file_name)
            os.makedirs(pdf_output_dir, exist_ok=True)

            with open(pdf_path, 'rb') as book:
                pdfReader = PdfReader(book)
                text = ''
                for page in pdfReader.pages:
                    text += page.extract_text() or ''  # Add or '' to handle None return on empty pages

            # Save the audio file in the subfolder
            audio_file_path = os.path.join(pdf_output_dir, f'{pdf_file_name}.mp3')
            speaker.save_to_file(text, audio_file_path)
            speaker.runAndWait()

            # Save the transcript in the subfolder
            transcript_file_path = os.path.join(pdf_output_dir, f'{pdf_file_name}.txt')
            with open(transcript_file_path, 'w', encoding='utf-8') as transcript_file:
                transcript_file.write(text)

            # Emit the completion signal with the path of the subfolder
            self.conversion_complete_signal.emit(pdf_output_dir)
        except Exception as e:
            self.conversion_complete_signal.emit(str(e))  # Emit the error


    def on_conversion_complete(self, output_subfolder_path):
        QMessageBox.information(self, "Conversion Complete", "The PDF has been converted to MP3.")
        self.open_output_folder(output_subfolder_path)
        self.convert_button.setEnabled(True)  # Re-enable the convert button

    def open_output_folder(self, path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', path])
        else:  # Linux
            subprocess.Popen(['xdg-open', path])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFtoMP3Converter()
    window.show()
    sys.exit(app.exec_())
