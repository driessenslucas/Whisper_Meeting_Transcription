import os
from google.cloud import storage
from faster_whisper import WhisperModel
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment

# Load environment variables from a .env file
load_dotenv()

# Initialize OpenAI API client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Cloud Storage bucket details
# Replace the bucket_name with the name of your GCS bucket where the audio files are stored
bucket_name = ""
audio_files_folder = "audio_files"
summaries_folder = "summaries"
processed_audio_files_folder = "processed_audio_files"

# Whisper model initialization
model_size = "large-v3"
model = WhisperModel(model_size, compute_type="int8", cpu_threads=6)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def move_blob(bucket_name, source_blob_name, destination_blob_name):
    """Moves a blob to a new location within the same bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    new_blob = bucket.rename_blob(blob, destination_blob_name)
    print(f"Blob {source_blob_name} moved to {destination_blob_name}.")

def convert_to_wav(source_file_path, target_file_path):
    """Converts various audio file formats to .wav using pydub."""
    audio = AudioSegment.from_file(source_file_path)
    audio.export(target_file_path, format="wav")
    print(f"Converted {source_file_path} to {target_file_path}.")

def transcribe_audio(file_path):
    """Transcribes the audio file using Whisper model."""
    segments, info = model.transcribe(file_path, beam_size=5)
    transcription = ""
    for segment in segments:
        transcription += f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
    print(f"Transcription completed. Detected language: {info.language} with probability {info.language_probability}.")
    
    return transcription

def summarize_text(text):
    """Summarizes the given text using OpenAI API."""
    PROMPT = f"""
    ---
    Vergadering:

    {text}

    ---

    Samenvatting:
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
            You are a meeting assistant. Your task is to take structured notes during a meeting, without mentioning who said what.
            You are a Dutch meeting assistant. Everything you read and write is in Dutch.
            """},
            {"role": "user", "content": PROMPT},
        ]
    )
    summary = completion.choices[0].message.content
    print("Summary created.")
    
    return summary

def process_meeting(file_name):
    local_audio_path = f"/tmp/{file_name}"
    local_wav_path = "/tmp/audio.wav"
    local_transcription_path = "/tmp/transcription.txt"
    local_summary_path = "/tmp/summary.txt"

    # Download the audio file from the source bucket
    download_blob(bucket_name, f"{audio_files_folder}/{file_name}", local_audio_path)

    # Convert the audio file to .wav format
    convert_to_wav(local_audio_path, local_wav_path)

    # Transcribe the audio file
    transcription = transcribe_audio(local_wav_path)

    # Save the transcription to a local file
    with open(local_transcription_path, "w") as f:
        f.write(transcription)

    # Summarize the transcription
    summary = summarize_text(transcription)

    # Save the summary to a local file
    with open(local_summary_path, "w") as f:
        f.write(summary)

    # Upload the transcription and summary to the destination bucket
    upload_blob(bucket_name, local_transcription_path, f"transcriptions/{file_name}.txt")
    upload_blob(bucket_name, local_summary_path, f"{summaries_folder}/{file_name}.txt")

    # Move the processed audio file to a "processed" subfolder
    move_blob(bucket_name, f"{audio_files_folder}/{file_name}", f"{processed_audio_files_folder}/{file_name}")

    # Clean up local files
    os.remove(local_audio_path)
    os.remove(local_wav_path)
    os.remove(local_transcription_path)
    os.remove(local_summary_path)

def process_all_meetings():
    """Processes all audio files in the source bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=audio_files_folder)

    for blob in blobs:
        file_name = blob.name[len(audio_files_folder) + 1:]  # Remove the folder prefix
        if not file_name.endswith("/") and not file_name.startswith("processed/"):  # Skip directories and already processed files
            print(f"Processing file: {file_name}")
            process_meeting(file_name)

# Start processing all meetings
process_all_meetings()
