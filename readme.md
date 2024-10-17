# Audio Processing with Whisper and OpenAI

This project provides a solution for processing audio files stored in a Google Cloud Storage (GCS) bucket. The script downloads audio files, converts them to WAV format, transcribes the audio using the Whisper model, summarizes the transcriptions with OpenAI's API, and then uploads the results back to the GCS bucket. 

> Note this is using a local implementation of whisper, depending on your machine it will be very slow

## Features

- Downloads audio files from a specified GCS bucket.
- Converts various audio formats to WAV.
- Transcribes audio files using the Whisper model.
- Summarizes transcriptions using OpenAI's GPT model.
- Moves processed audio files to a designated folder in GCS.

## Prerequisites

- Python 3.7 or higher
- Access to a Google Cloud account with Cloud Storage enabled
- An OpenAI account and API key
- Required Python packages

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/driessenslucas/Whisper_Meeting_Transcription.git
   cd Whisper_Meeting_Transcription
   ```

2. Create a `.env` file in the project root and add your API keys and bucket name:

   ```dotenv
   OPENAI_API_KEY=<your-openai-api-key>
   BUCKET_NAME=<your-gcs-bucket-name>
   ```

3. Install the required dependencies:

   ```bash
   pip install google-cloud-storage faster-whisper openai python-dotenv pydub
   ```

4. Set up your Google Cloud credentials:

   Ensure that you have set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to your service account key JSON file.

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
   ```

## Usage

To process all audio files in the specified GCS bucket, run the script:

```bash
python your_script_name.py
```

### Functionality Overview

- **`download_blob(bucket_name, source_blob_name, destination_file_name)`**: Downloads an audio file from GCS.
- **`upload_blob(bucket_name, source_file_name, destination_blob_name)`**: Uploads processed files (transcriptions and summaries) back to GCS.
- **`move_blob(bucket_name, source_blob_name, destination_blob_name)`**: Moves processed audio files to a "processed" folder within the GCS bucket.
- **`convert_to_wav(source_file_path, target_file_path)`**: Converts audio files to WAV format using the `pydub` library.
- **`transcribe_audio(file_path)`**: Transcribes audio files using the Whisper model.
- **`summarize_text(text)`**: Generates a summary of the transcription using OpenAI's GPT model.
- **`process_meeting(file_name)`**: Coordinates the downloading, processing, and uploading of each audio file.
- **`process_all_meetings()`**: Iterates through all audio files in the source bucket and processes them.

## Environment Variables

Make sure to define the following environment variables in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `BUCKET_NAME`: The name of your GCS bucket where the audio files are stored.

## Notes

- Ensure that the audio files are stored in the `audio_files` folder within your GCS bucket.
- Processed transcriptions will be saved in the `transcriptions` folder, and summaries will be saved in the `summaries` folder.
- Processed audio files will be moved to the `processed_audio_files` folder.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [Google Cloud Storage](https://cloud.google.com/storage)
- [OpenAI](https://openai.com/)
- [Faster Whisper](https://github.com/guillaumeleclercq/faster-whisper)
- [pydub](https://github.com/jiaaro/pydub)
