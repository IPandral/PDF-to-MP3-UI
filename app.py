import sys
import os
import subprocess
import pyttsx3
import requests
import webbrowser
from PyPDF2 import PdfReader
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QAction
)
from PyQt5.QtGui import QDesktopServices
from threading import Thread

# Define a stylesheet
stylesheet = """
    QPushButton {
        background-color: #333;
        color: #fff;
        border-radius: 10px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #666;
    }
    QLabel {
        color: #333;
        font-size: 16px;
    }
"""

class PDFtoMP3Converter(QMainWindow):
    conversion_complete_signal = pyqtSignal(str)  # Signal to indicate conversion is complete

    def __init__(self):
        super().__init__()

        self.check_for_updates()
        self.setAcceptDrops(True)
        self.setWindowTitle("PDF to MP3")
        self.setGeometry(100, 100, 280, 170)

        layout = QVBoxLayout()

        self.help_action = QAction('Help', self)
        self.help_action.triggered.connect(self.open_user_manual)

        self.license_action = QAction('License', self)
        self.license_action.triggered.connect(lambda: webbrowser.open('https://github.com/IPandral/PDF-to-MP3-UI/blob/main/LICENSE'))

        self.about_action = QAction('About', self)
        self.about_action.triggered.connect(lambda: webbrowser.open('https://github.com/IPandral/PDF-to-MP3-UI/wiki/About'))

        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu('Help')
        help_menu.addAction(self.help_action)

        license_menu = menu_bar.addMenu('License')
        license_menu.addAction(self.license_action)

        about_menu = menu_bar.addMenu('About')
        about_menu.addAction(self.about_action)

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

    def check_for_updates(self):
        response = requests.get('https://api.github.com/repos/IPandral/PDF-to-MP3-UI/releases/latest')
        latest_version = response.json()['tag_name']

        current_version = 'v1.0.3'  # Replace with your current version

        if latest_version != current_version:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Update available")
            msg_box.setText(f"A new version ({latest_version}) is available.")
            download_button = msg_box.addButton("Download", QMessageBox.ActionRole)
            download_button.clicked.connect(self.open_download_link)
            msg_box.addButton("Skip for now", QMessageBox.RejectRole)
            msg_box.exec_()

    def open_download_link(self):
        QDesktopServices.openUrl(QUrl("https://github.com/IPandral/PDF-to-MP3-UI/releases/latest"))

    def dragEnterEvent(self, event):
        # Accept the drag event if the dragged item is a PDF file
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toLocalFile()
            if url.endswith('.pdf'):
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Get the path of the dropped PDF file
        url = event.mimeData().urls()[0].toLocalFile()
        self.pdf_file_path = url
        self.pdf_path_label.setText(f"Selected PDF: {os.path.basename(url)}")

        # Set the output directory to the directory of the input file if no output directory has been selected yet
        if not hasattr(self, 'output_dir_path') or not self.output_dir_path:
            self.output_dir_path = os.path.dirname(url)
            self.output_path_label.setText(f"Output Folder: {os.path.dirname(url)}")

    def select_pdf(self):
        pdf_file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF files (*.pdf)")
        if pdf_file:
            self.pdf_path_label.setText(pdf_file)
            self.pdf_file_path = pdf_file

            # Set the output directory to the directory of the input file if no output directory has been selected yet
            if not hasattr(self, 'output_dir_path') or not self.output_dir_path:
                self.output_dir_path = os.path.dirname(pdf_file)
                self.output_path_label.setText(f"Output Folder: {os.path.dirname(pdf_file)}")

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
    
    def open_user_manual(self):
        webbrowser.open('https://github.com/IPandral/PDF-to-MP3-UI/wiki/User-Manual-for-PDF-to-MP3-Converter')

if __name__ == '__main__':
    # Create a QApplication instance and apply the stylesheet
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)

    # Create an instance of your application and show it
    window = PDFtoMP3Converter()
    window.show()

    # Run the application
    sys.exit(app.exec_())