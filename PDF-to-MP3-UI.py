import sys
import os
import subprocess
import pyttsx3
import requests
import webbrowser
from PyPDF2 import PdfReader
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QAction, QTextEdit
from PyQt5.QtGui import QDesktopServices
from threading import Thread
import vlc

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

        # Create a QTextEdit widget for displaying PDF text
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setGeometry(10, 100, 780, 500)

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

        clear_action = QAction('Clear Fields', self)
        clear_action.triggered.connect(self.clear_fields)
        clear_menu = menu_bar.addMenu('Clear')
        clear_menu.addAction(clear_action)

        self.title_label = QLabel("PDF to MP3", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.pdf_path_label = QLabel("Select a PDF file", self)
        layout.addWidget(self.pdf_path_label)

        self.select_pdf_button = QPushButton("Select PDF File", self)
        self.select_pdf_button.clicked.connect(self.select_pdf)
        layout.addWidget(self.select_pdf_button)

        self.pdf_folder_path = QLabel("Select a folder of PDF's", self)
        layout.addWidget(self.pdf_folder_path)

        self.select_pdf_folder_button = QPushButton("Select a folder of PDF's", self)
        self.select_pdf_folder_button.clicked.connect(self.select_pdf_folder)
        layout.addWidget(self.select_pdf_folder_button)

        self.output_path_label = QLabel("Select Output Folder", self)
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
    
    def play_audio(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText('Play')
        else:
            if self.pdf_file_path and self.output_dir_path:
                pdf_file_name = os.path.basename(self.pdf_file_path)
                base_name = os.path.splitext(pdf_file_name)[0]
                audio_file_path = os.path.join(self.output_dir_path, f'{base_name}.mp3')
                if os.path.exists(audio_file_path):
                    self.media_player.set_media(vlc.Media(audio_file_path))
                    self.media_player.play()
                    self.play_button.setText('Pause')
                else:
                    QMessageBox.warning(self, "File Not Found", "The corresponding MP3 file was not found.")
            else:
                QMessageBox.warning(self, "No File Selected", "Please select a PDF file and output directory first.")

    def on_conversion_complete(self, output_dir_path):
        # Assuming the .txt file has the same name as the PDF, find the first .txt file in the output directory
        for file in os.listdir(output_dir_path):
            if file.endswith('.txt'):
                txt_file_path = os.path.join(output_dir_path, file)
                self.load_text_file(txt_file_path)
                break

    def load_text_file(self, file_path):
        # Read from the .txt file and display its contents
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                self.text_display.setText(text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load text file: {e}")

    def check_for_updates(self):
        response = requests.get('https://api.github.com/repos/IPandral/PDF-to-MP3-UI/releases/latest')
        latest_version = response.json()['tag_name']

        current_version = 'v1.0.6'  # Replace with your current version

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

    def select_pdf_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select PDF Folder")
        if folder_path:  # if user didn't pick a directory don't continue
            self.pdf_folder_path.setText(f"Selected PDF Folder: {folder_path}")
            self.pdf_file_path = folder_path

            # Set the output directory to the selected folder if no output directory has been selected yet
            if not hasattr(self, 'output_dir_path') or not self.output_dir_path:
                self.output_dir_path = folder_path
                self.output_path_label.setText(f"Output Folder: {folder_path}")

    def select_output(self):
        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_path:
            self.output_path_label.setText(output_path)
            self.output_dir_path = output_path

    def clear_fields(self):
        self.pdf_path_label.setText("Select a PDF file")
        self.pdf_folder_path.setText("Select a folder of PDF's")
        self.output_path_label.setText("Select Output Folder")
        self.pdf_file_path = ""
        self.output_dir_path = ""

    def convert(self):
        if self.pdf_file_path and self.output_dir_path:
            self.convert_button.setEnabled(False)  # Disable the button while processing

            # Check if the selected path is a directory
            if os.path.isdir(self.pdf_file_path):
                # Loop over all PDF files in the directory
                for filename in os.listdir(self.pdf_file_path):
                    if filename.endswith('.pdf'):
                        pdf_file_path = os.path.join(self.pdf_file_path, filename)
                        # Run the conversion in a separate thread to avoid freezing the UI
                        conversion_thread = Thread(target=self.convert_pdf_to_mp3, args=(pdf_file_path, self.output_dir_path))
                        conversion_thread.start()
            else:
                # Run the conversion in a separate thread to avoid freezing the UI
                conversion_thread = Thread(target=self.convert_pdf_to_mp3, args=(self.pdf_file_path, self.output_dir_path))
                conversion_thread.start()

    def convert_pdf_to_mp3(self, pdf_path, output_dir):
        try:
            speaker = pyttsx3.init()
            pdf_file = os.path.basename(pdf_path)
            pdf_file_name = os.path.splitext(pdf_file)[0]  # Get the file name without the extension

            # Create a single output directory for all conversions
            output_dir_name = "Converted_PDFs"
            output_dir_path = os.path.join(output_dir, output_dir_name)
            counter = 1
            while os.path.exists(output_dir_path):
                output_dir_path = os.path.join(output_dir, f"{output_dir_name}_{counter}")
                counter += 1
            os.makedirs(output_dir_path, exist_ok=True)

            with open(pdf_path, 'rb') as book:
                pdfReader = PdfReader(book)
                text = ''
                for page in pdfReader.pages:
                    text += page.extract_text() or ''  # Add or '' to handle None return on empty pages

            # Save the audio file in the output directory
            audio_file_path = os.path.join(output_dir_path, f'{pdf_file_name}.mp3')
            speaker.save_to_file(text, audio_file_path)
            speaker.runAndWait()

            # Save the transcript in the output directory
            transcript_file_path = os.path.join(output_dir_path, f'{pdf_file_name}.txt')
            with open(transcript_file_path, 'w', encoding='utf-8') as transcript_file:
                transcript_file.write(text)

            # Emit the completion signal with the path of the output directory
            self.conversion_complete_signal.emit(output_dir_path)
        except Exception as e:
            self.conversion_complete_signal.emit(str(e))  # Emit the error


    def on_conversion_complete(self, output_dir_path):
        result = QMessageBox.question(self, "Conversion Complete", "The conversion is complete. Do you want to open the audio player?", QMessageBox.Yes | QMessageBox.No)
        
        if result == QMessageBox.Yes:
            if self.pdf_file_path:
                pdf_file_name = os.path.basename(self.pdf_file_path)
                base_name = os.path.splitext(pdf_file_name)[0]
                audio_file_path = os.path.join(output_dir_path, f'{base_name}.mp3')
                
                self.audio_player_window = AudioPlayerWindow(audio_file_path)
                self.audio_player_window.show()

    def open_output_folder(self, path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', path])
        else:  # Linux
            subprocess.Popen(['xdg-open', path])
    
    def open_user_manual(self):
        webbrowser.open('https://github.com/IPandral/PDF-to-MP3-UI/wiki/User-Manual-for-PDF-to-MP3-Converter')

class AudioPlayerWindow(QMainWindow):
    def __init__(self, audio_file_path, parent=None):
        super().__init__(parent)

        self.media_player = vlc.MediaPlayer()
        self.audio_file_path = audio_file_path

        self.setWindowTitle("Audio Player")
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_audio_playback)
        layout.addWidget(self.play_button)

        self.restart_button = QPushButton("Restart", self)
        self.restart_button.clicked.connect(self.restart_audio)
        layout.addWidget(self.restart_button)

        self.backward_button = QPushButton("Backward 10s", self)
        self.backward_button.clicked.connect(self.backward_audio)
        layout.addWidget(self.backward_button)

        self.forward_button = QPushButton("Forward 10s", self)
        self.forward_button.clicked.connect(self.forward_audio)
        layout.addWidget(self.forward_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def toggle_audio_playback(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText('Play')
        else:
            if not self.media_player.get_media():
                self.media_player.set_media(vlc.Media(self.audio_file_path))
            self.media_player.play()
            self.play_button.setText('Pause')

    def restart_audio(self):
        self.media_player.stop()
        self.play_button.setText('Play')

    def backward_audio(self):
        if self.media_player.is_playing() or self.media_player.get_time() > 0:
            # Go back 10 seconds
            new_time = max(self.media_player.get_time() - 10000, 0)
            self.media_player.set_time(new_time)

    def forward_audio(self):
        if self.media_player.is_playing() or self.media_player.get_time() > 0:
            # Go forward 10 seconds
            total_length = self.media_player.get_length()
            new_time = min(self.media_player.get_time() + 10000, total_length)
            self.media_player.set_time(new_time)

    def closeEvent(self, event):
        # This method is called when the window is closed
        if self.media_player.is_playing():
            self.media_player.stop()
        event.accept()  # Accept the close event

if __name__ == '__main__':
    # Create a QApplication instance and apply the stylesheet
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)

    # Create an instance of your application and show it
    window = PDFtoMP3Converter()
    window.show()

    # Run the application
    sys.exit(app.exec_())

#Last updated: Tuesday, 02. January 2024 21:31, +08:00