# PDF-to-MP3-UI
 
This repository contains a Python script that converts the text content of a PDF file into an MP3 file. This can be particularly useful for students or anyone who prefers to listen to text rather than read it, such as people with visual impairments or those who want to consume content while doing other tasks.

I personally created this application to turn my university assigment PDF into voice as i find it easier to understand.

## How it works

The script uses the PyPDF2 library to extract text from the PDF files and the pyttsx3 library to convert the extracted text into speech. The speech is then saved as an MP3 file. In addition, a transcript of the text is saved as a .txt file.

## Usage

1. Place your PDF files in the `input` directory.
2. Run the `app.py` script.
3. The script will create a separate folder for each PDF file in the `output` directory. Each folder will contain an MP3 file and a .txt transcript file.

## Requirements

- Python 3.6 or higher
- PyPDF2
- pyttsx3

You can install the required Python libraries using pip:

```bash
pip install PyPDF2 pyttsx3
```

## License

This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.
