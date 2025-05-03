import os
from flask import Flask, request, render_template
import whisper
from api.summarize import summarize_text

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

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload started")
    try:
        if 'audio_file' not in request.files:
            return render_template('error.html', message="No file part found. Please upload a valid audio file.")

        file = request.files['audio_file']
        if file.filename == '':
            return render_template('error.html', message="No file selected. Please choose an audio file to upload.")

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
                return render_template('error.html', message="No text was transcribed from the audio file.")

            summarized_text = summarize_text(transcribed_text)
            print(f"Summary: {summarized_text}")

            return render_template('result.html', transcription=transcribed_text, summary=summarized_text)

        else:
            return render_template('error.html', message="Invalid file type or Whisper model not loaded.")
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        return render_template('error.html', message=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    import traceback
    app.run(debug=True)
