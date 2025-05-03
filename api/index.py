import os
from flask import Flask, request, render_template
import whisper
from summarize import summarize_text
import traceback  # <-- Added this import for traceback

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

app = Flask(__name__, template_folder='../templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = whisper.load_model("base.en")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload started")
    try:
        if 'audio_file' not in request.files:
            return render_template('error.html', message="No file part found. Please upload a valid audio file.")

        file = request.files['audio_file']
        if file.filename == '':
            return render_template('error.html', message="No file selected. Please choose an audio file to upload.")

        # Check if the file size is within the allowed limit
        file.seek(0, os.SEEK_END)  # Move to the end of the file
        file_size = file.tell()  # Get file size
        file.seek(0)  # Reset the pointer to the beginning of the file

        if file_size > MAX_FILE_SIZE:
            return render_template('error.html', message="File is too large. Please upload a smaller audio file (max 10MB).")

        if file and allowed_file(file.filename) and model:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            print("Starting transcription...")
            result = model.transcribe(filepath)
            print("Finished transcription")
            transcribed_text = result.get('text', '').strip()
            print(f"Transcribed: {transcribed_text}")

            if not transcribed_text:
                return render_template('error.html', message="We couldn't detect any speech in your audio. Please try again with a clearer recording.")

            summarized_text = summarize_text(transcribed_text)
            print(f"Summary: {summarized_text}")

            return render_template('result.html', transcription=transcribed_text, summary=summarized_text)

        else:
            return render_template('error.html', message="Unsupported file type. Please upload a valid audio file (e.g., .mp3, .wav, .m4a).")

    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        return render_template('error.html', message=f"An unexpected error occurred: {str(e)}. Please try again.")

if __name__ == '__main__':
    app.run(debug=True)
