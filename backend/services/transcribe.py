from faster_whisper import WhisperModel
from backend.config import settings
from backend.services.email import send_mail

# faster-whisper: 4x faster, uses less memory, perfect for Pi 5
model = WhisperModel(
    settings.whisper_model,
    device="cpu",
    compute_type="int8"  # Optimized for CPU inference
)

def transcribe_audio(file_path):
    """
    Transcribes audio from a given file and sends the transcription via email.

    The function processes an audio file specified by its path, transcribes the
    audio contents into text format, and sends the transcribed text to a
    predefined mail recipient via email.

    :param file_path: Path to the audio file to be transcribed.
    :type file_path: str
    :param job_id: Unique identifier for the transcription job.
    :type job_id: str
    :return: The transcribed text from the audio file.
    :rtype: str
    """

    segments, info = model.transcribe(file_path)
    transcription_text = " ".join([segment.text for segment in segments])
    send_mail(transcription_text)
    return transcription_text