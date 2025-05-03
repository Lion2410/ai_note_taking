import os
from dotenv import load_dotenv
import asyncio
from flask import Flask, request, render_template
from deepgram import Deepgram
from summarize import summarize_text  # Your sumy-based summarizer

load_dotenv()  # This loads the .env file
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Flask config
app = Flask(__name__, template_folder='../templates')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Deepgram setup
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY environment variable not set.")
dg_client = Deepgram(DEEPGRAM_API_KEY)

# Route for home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'audio_file' not in request.files:
            return render_template('error.html', message="No file part found.")

        file = request.files['audio_file']
        if file.filename == '':
            return render_template('error.html', message="No file selected.")

        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Transcription using Deepgram
        async def transcribe():
            with open(filepath, 'rb') as audio:
                source = {
                    'buffer': audio,
                    'mimetype': file.content_type
                }
                response = await dg_client.transcription.prerecorded(
                    source,
                    {'punctuate': True, 'language': 'en-US'}
                )
                return response['results']['channels'][0]['alternatives'][0]['transcript']

        transcribed_text = asyncio.run(transcribe()).strip()
        os.remove(filepath)  # Clean up

        if not transcribed_text:
            return render_template('error.html', message="No speech detected in the audio.")

        summarized_text = summarize_text(transcribed_text)

        return render_template('result.html', transcription=transcribed_text, summary=summarized_text)

    except Exception as e:
        return render_template('error.html', message=f"An error occurred: {str(e)}")

# Run app
if __name__ == '__main__':
    app.run(debug=True)
