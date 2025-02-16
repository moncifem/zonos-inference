from flask import Flask, request, jsonify
import torch
import torchaudio
import os
import tempfile
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=device)
    return model

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        text = data.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Handle audio file
        audio_data = data.get('audio')
        if not audio_data:
            return jsonify({"error": "No audio data provided"}), 400

        # Decode base64 audio
        try:
            audio_bytes = base64.b64decode(audio_data)
        except:
            return jsonify({"error": "Invalid audio data format"}), 400

        # Save temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_audio.write(audio_bytes)
            audio_path = temp_audio.name

        # Load audio and generate speech
        wav, sampling_rate = torchaudio.load(audio_path)
        speaker = model.make_speaker_embedding(wav, sampling_rate)
        
        cond_dict = make_cond_dict(text=text, speaker=speaker, language="en-us")
        conditioning = model.prepare_conditioning(cond_dict)
        
        codes = model.generate(conditioning)
        wavs = model.autoencoder.decode(codes).cpu()
        
        # Save output to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
            torchaudio.save(temp_output.name, wavs[0], model.autoencoder.sampling_rate)
            
            # Read the file and convert to base64
            with open(temp_output.name, 'rb') as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')

        # Cleanup temporary files
        os.unlink(audio_path)
        os.unlink(temp_output.name)

        return jsonify({
            "status": "success",
            "audio": audio_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Load model at startup
    model = load_model()
    app.run(host='0.0.0.0', port=5000) 