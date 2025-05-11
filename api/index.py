import os
from flask import Flask, request, render_template
from dotenv import load_dotenv
from deepgram import DeepgramClient
from summarize import summarize_text
import mimetypes
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Add this at the top of index.py
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY not found in environment variables")

# Initialize Deepgram client (v4 SDK)
dg_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)

# Flask app setup
app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
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
            if len(file.read()) > MAX_FILE_SIZE:
                return render_template('error.html', message="File too large. Maximum size is 10MB.")
            file.seek(0)  # Reset file pointer after reading
            file.save(filepath)
            logging.debug(f"File saved to: {filepath}")

            # Detect the MIME type of the uploaded file
            mimetype, _ = mimetypes.guess_type(filepath)
            logging.debug(f"Detected MIME type: {mimetype}")

            # Use Deepgram v4 SDK to transcribe
            with open(filepath, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                logging.debug(f"Audio bytes length: {len(audio_bytes)}")

            # Configure Deepgram options (v4 syntax)
            options = {
                "model": "nova-2",
                "language": "en",
                "smart_format": True
            }

            # v4 API call for pre-recorded transcription
            response = dg_client.listen.rest.v("1").transcribe_file(
                {"buffer": audio_bytes, "mimetype": mimetype or "audio/mpeg"},
                options
            )
            logging.debug(f"Deepgram response: {response}")

            transcription = response.results.channels[0].alternatives[0].transcript
            logging.debug(f"Transcription: {transcription}")

            if not transcription:
                return render_template('error.html', message="No speech detected. Please upload a clearer recording.")

            summary = summarize_text(transcription)
            logging.debug(f"Summary: {summary}")

            return render_template('result.html', transcription=transcription, summary=summary)

        return render_template('error.html', message="Unsupported file type. Please upload .mp3, .wav, or .m4a.")

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        return render_template('error.html', message=f"An error occurred: {str(e)}")

# Vercel requires a handler for serverless functions
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)