import torch
import torchaudio
import os
from zonos.model import Zonos
from zonos.conditioning import make_cond_dict
from zonos.utils import DEFAULT_DEVICE as device

class AudioService:
    def __init__(self, model_type="transformer"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        self.model = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=self.device)

    def generate_speech(self, text: str, speaker_file: str, language: str = "en-us") -> str:
        """
        Generate speech from text using a speaker reference file
        Args:
            text (str): Text to convert to speech
            speaker_file (str): Path to speaker reference audio file
            language (str): Language code (e.g., "en-us", "ja-jp", "zh-cn", "fr-fr", "de-de")
        Returns:
            str: Path to generated audio file
        """
        wav, sampling_rate = torchaudio.load(speaker_file)
        speaker = self.model.make_speaker_embedding(wav, sampling_rate)
        cond_dict = make_cond_dict(text=text, speaker=speaker, language=language)
        conditioning = self.model.prepare_conditioning(cond_dict)
        codes = self.model.generate(conditioning)
        wavs = self.model.autoencoder.decode(codes).cpu()
        output_path = f"generated_{hash(text)}_{hash(speaker_file)}.wav"
        torchaudio.save(output_path, wavs[0], self.model.autoencoder.sampling_rate)
        return output_path 