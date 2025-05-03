import os
from flask import Flask, request, render_template
from dotenv import load_dotenv  # Import to load environment variables from .env file
import asyncio  # Import for handling asynchronous tasks
from deepgram import Deepgram
from summarize import summarize_text

# Load environment variables from .env file
load_dotenv()

# Your API key, set from environment variables
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

# Instantiate Deepgram client correctly (with the updated version)
dg_client = Deepgram(DEEPGRAM_API_KEY)

app = Flask(__name__, template_folder='../templates')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

# Update this in the `upload_file` function:
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
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            # Initialize the Deepgram client using the correct method
            dg_client = Deepgram(DEEPGRAM_API_KEY)

            # Use the new transcription method for version 3
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            with open(filepath, 'rb') as audio_file:
                response = loop.run_until_complete(dg_client.transcription.sync_prerecorded(audio_file, {'language': 'en'}))

            transcription = response['results']['channels'][0]['alternatives'][0]['transcript']

            # Handle transcription failure
            if not transcription:
                return render_template('error.html', message="We couldn't detect any speech in your audio. Please try again with a clearer recording.")

            # Summarize the transcription
            summarized_text = summarize_text(transcription)

            return render_template('result.html', transcription=transcription, summary=summarized_text)

        else:
            return render_template('error.html', message="Unsupported file type. Please upload a valid audio file (e.g., .mp3, .wav, .m4a).")

    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the port Render provides
    app.run(host='0.0.0.0', port=port, debug=True)

