import sys
import os
import subprocess
import requests
import webbrowser
from PyPDF2 import PdfReader
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QAction, QSlider
from PyQt5.QtGui import QDesktopServices
from threading import Thread
import vlc
from gtts import gTTS

class PDFtoMP3Converter(QMainWindow):
    conversion_complete_signal = pyqtSignal(str)  # Signal to indicate conversion is complete

    def __init__(self):
        super().__init__()

        self.check_for_updates()
        self.setAcceptDrops(True)
        self.setWindowTitle("PDF to MP3")
        self.setGeometry(100, 100, 280, 220)

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

        self.pdf_folder_path = QLabel("Select a folder of PDFs", self)
        layout.addWidget(self.pdf_folder_path)

        self.select_pdf_folder_button = QPushButton("Select a folder of PDFs", self)
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

        self.open_mp3_button = QPushButton("Open MP3", self)
        self.open_mp3_button.clicked.connect(self.open_mp3)
        layout.addWidget(self.open_mp3_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.pdf_file_path = None
        self.output_dir_path = None

        self.conversion_complete_signal.connect(self.on_conversion_complete)

    def check_for_updates(self):
        try:
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
        except Exception as e:
            print(f"Error checking for updates: {e}")

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
        if not self.output_dir_path:
            self.output_dir_path = os.path.dirname(url)
            self.output_path_label.setText(f"Output Folder: {os.path.dirname(url)}")

    def select_pdf(self):
        pdf_file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF files (*.pdf)")
        if pdf_file:
            self.pdf_path_label.setText(pdf_file)
            self.pdf_file_path = pdf_file

            # Set the output directory to the directory of the input file if no output directory has been selected yet
            if not self.output_dir_path:
                self.output_dir_path = os.path.dirname(pdf_file)
                self.output_path_label.setText(f"Output Folder: {os.path.dirname(pdf_file)}")

    def select_pdf_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select PDF Folder")
        if folder_path:  # if user didn't pick a directory don't continue
            self.pdf_folder_path.setText(f"Selected PDF Folder: {folder_path}")
            self.pdf_file_path = folder_path

            # Set the output directory to the selected folder if no output directory has been selected yet
            if not self.output_dir_path:
                self.output_dir_path = folder_path
                self.output_path_label.setText(f"Output Folder: {folder_path}")

    def select_output(self):
        output_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_path:
            self.output_path_label.setText(output_path)
            self.output_dir_path = output_path

    def clear_fields(self):
        self.pdf_path_label.setText("Select a PDF file")
        self.pdf_folder_path.setText("Select a folder of PDFs")
        self.output_path_label.setText("Select Output Folder")
        self.pdf_file_path = ""
        self.output_dir_path = ""

    def convert(self):
        if self.pdf_file_path and self.output_dir_path:
            self.convert_button.setEnabled(False)  # Disable the button while processing
            # Run the conversion in a separate thread to avoid freezing the UI
            conversion_thread = Thread(target=self.run_conversion)
            conversion_thread.start()

    def run_conversion(self):
        try:
            # Check if the selected path is a directory
            if os.path.isdir(self.pdf_file_path):
                # Loop over all PDF files in the directory
                for filename in os.listdir(self.pdf_file_path):
                    if filename.endswith('.pdf'):
                        pdf_file_path = os.path.join(self.pdf_file_path, filename)
                        self.convert_pdf_to_mp3(pdf_file_path, self.output_dir_path)
            else:
                self.convert_pdf_to_mp3(self.pdf_file_path, self.output_dir_path)
        except Exception as e:
            self.conversion_complete_signal.emit(str(e))
        finally:
            self.convert_button.setEnabled(True)  # Re-enable the button after processing

    def convert_pdf_to_mp3(self, pdf_path, output_dir):
        try:
            print(f"Starting conversion for: {pdf_path}")
            pdf_file = os.path.basename(pdf_path)
            pdf_file_name = os.path.splitext(pdf_file)[0]

            output_dir_path = os.path.join(output_dir, "Converted_PDFs")
            if not os.path.exists(output_dir_path):
                os.makedirs(output_dir_path, exist_ok=True)
            print(f"Output directory: {output_dir_path}")

            audio_file_path = os.path.join(output_dir_path, f'{pdf_file_name}.mp3')
            transcript_file_path = os.path.join(output_dir_path, f'{pdf_file_name}.txt')
            print(f"Audio file path: {audio_file_path}")
            print(f"Transcript file path: {transcript_file_path}")

            with open(pdf_path, 'rb') as book:
                pdfReader = PdfReader(book)
                text = ''.join(page.extract_text() or '' for page in pdfReader.pages)
            print(f"Extracted text length: {len(text)}")

            tts = gTTS(text)
            tts.save(audio_file_path)
            print(f"Audio file saved: {audio_file_path}")

            with open(transcript_file_path, 'w', encoding='utf-8') as transcript_file:
                transcript_file.write(text)
            print(f"Transcript file saved: {transcript_file_path}")

            self.conversion_complete_signal.emit(output_dir_path)
        except Exception as e:
            print(f"Error during conversion: {e}")
            self.conversion_complete_signal.emit(str(e))

    def on_conversion_complete(self, output_dir_path):
        result = QMessageBox.question(self, "Conversion Complete", "The conversion is complete. Do you want to open the audio player?", QMessageBox.Yes | QMessageBox.No)
        
        if result == QMessageBox.Yes:
            if self.pdf_file_path:
                pdf_file_name = os.path.basename(self.pdf_file_path)
                base_name = os.path.splitext(pdf_file_name)[0]
                audio_file_path = os.path.join(output_dir_path, f'{base_name}.mp3')
                self.audio_player_window = AudioPlayerWindow(audio_file_path)
                self.audio_player_window.show()
        else:
            self.convert_button.setEnabled(True)

    def open_output_folder(self, path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', path])
        else:  # Linux
            subprocess.Popen(['xdg-open', path])

    def open_user_manual(self):
        webbrowser.open('https://github.com/IPandral/PDF-to-MP3-UI/wiki/User-Manual-for-PDF-to-MP3-Converter')

    def open_mp3(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("MP3 files (*.mp3)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.audio_player_window = AudioPlayerWindow(file_path)
            self.audio_player_window.show()

class AudioPlayerWindow(QMainWindow):
    def __init__(self, audio_file_path=None, parent=None):
        super().__init__(parent)

        self.media_player = vlc.MediaPlayer()
        self.audio_file_path = audio_file_path

        self.setWindowTitle("Audio Player")
        self.setGeometry(300, 300, 300, 300)

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

        self.volume_controls = QLabel("Volume Controls", self)
        layout.addWidget(self.volume_controls)

        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)  # Default volume
        self.volume_slider.valueChanged.connect(self.set_volume)
        layout.addWidget(self.volume_slider)

        self.speed_controls = QLabel("Playback Speed Controls", self)
        layout.addWidget(self.speed_controls)

        # Speed slider
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMinimum(50)  # 0.5x speed
        self.speed_slider.setMaximum(200)  # 2.0x speed
        self.speed_slider.setValue(100)  # 1.0x speed
        self.speed_slider.valueChanged.connect(self.set_speed)
        layout.addWidget(self.speed_slider)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        if self.audio_file_path:
            self.media_player.set_media(vlc.Media(self.audio_file_path))

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

    def set_volume(self, volume):
        self.media_player.audio_set_volume(volume)

    def set_speed(self, speed):
        rate = speed / 100.0
        self.media_player.set_rate(rate)

    def closeEvent(self, event):
        # This method is called when the window is closed
        if self.media_player.is_playing():
            self.media_player.stop()
        event.accept()  # Accept the close event

if __name__ == '__main__':
    # Create a QApplication instance and apply the stylesheet
    app = QApplication(sys.argv)

    # Create an instance of your application and show it
    window = PDFtoMP3Converter()
    window.show()

    # Run the application
    sys.exit(app.exec_())

# Last updated: Tuesday, 02. January 2024 22:26, +08:00
