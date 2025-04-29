import os
from flask import Flask, render_template, request
import whisper
from summarize import summarize_text

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Load the Whisper model once
try:
    model = whisper.load_model("base")
except Exception as e:
    model = None
    print(f"Failed to load Whisper model: {e}")

# Allowed audio extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'mp4', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'audio_file' not in request.files:
            return render_template('error.html', message="No file part found. Please upload a valid audio file.")
        
        file = request.files['audio_file']

        if file.filename == '':
            return render_template('error.html', message="No file selected. Please choose an audio file to upload.")
         
        if file and allowed_file(file.filename) and model:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Transcribe audio
            result = model.transcribe(filepath)
            transcribed_text = result.get('text', '').strip()

            if not transcribed_text:
                return render_template('error.html', message="No text was transcribed from the audio file.")

            # Summarize transcribed text
            summarized_text = summarize_text(transcribed_text)

            return render_template('result.html', transcription=transcribed_text, summary=summarized_text)
        else:
            return render_template('error.html', message="Invalid file type or Whisper model not loaded.")
    
    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
