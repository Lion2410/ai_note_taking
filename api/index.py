import os
from flask import Flask, request, render_template
from dotenv import load_dotenv
import asyncio
from deepgram import Deepgram
from summarize import summarize_text
import mimetypes

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Initialize Deepgram client (v3 SDK usage is correct here)
dg_client = Deepgram(DEEPGRAM_API_KEY)

# Flask app setup
app = Flask(__name__, template_folder='../templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file types
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
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

        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Use Deepgram v3 SDK to transcribe
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Detect the MIME type of the uploaded file
            mimetype, _ = mimetypes.guess_type(filepath)

            with open(filepath, 'rb') as audio_file:
                audio_bytes = audio_file.read()

            response = loop.run_until_complete(
                dg_client.transcription.prerecorded(
                    {"buffer": audio_bytes, "mimetype": mimetype or "audio/mpeg"},
                    {"language": "en"}
                )
            )

            transcription = response['results']['channels'][0]['alternatives'][0]['transcript']

            if not transcription:
                return render_template('error.html', message="No speech detected. Please upload a clearer recording.")

            summary = summarize_text(transcription)

            return render_template('result.html', transcription=transcription, summary=summary)

        return render_template('error.html', message="Unsupported file type. Please upload .mp3, .wav, or .m4a.")

    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Port for Render or default
    app.run(host='0.0.0.0', port=port, debug=True)
