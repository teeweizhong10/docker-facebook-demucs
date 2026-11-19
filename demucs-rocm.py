from types import SimpleNamespace

import soundfile
from demucs import audio, separate


def save_lossless(path, samples, sample_rate, *, bits_per_sample, encoding=None):
    subtype = "FLOAT" if encoding == "PCM_F" else f"PCM_{bits_per_sample}"
    frames = samples.detach().cpu().transpose(0, 1).numpy()
    soundfile.write(path, frames, sample_rate, subtype=subtype)


if __name__ == "__main__":
    # Demucs applies its clipping settings before handing WAV and FLAC to this writer.
    # MP3 output and input decoding still use Demucs's existing paths.
    audio.ta = SimpleNamespace(save=save_lossless)
    separate.main()
