# Audio Transcription and Summarization Webapp - Setup Guide

This Flask web application provides audio transcription using WhisperX and AI-powered summarization for educational meeting recordings.

## Features

- **Audio Transcription**: Convert audio files to text using WhisperX models
- **Model Selection**: Choose from different WhisperX models (large-v2 recommended)
- **AI Summarization**: Generate structured summaries using language models
- **PDF Export**: Download summaries as formatted PDF documents
- **Support for Multiple Audio Formats**: Supports .mp3, .wav, .ogg, .m4a, .flac


## Installation and Setup

### Step 1: Install Miniconda
1. Download from: https://docs.conda.io/en/latest/miniconda.html
2. Run the installer
3. Check "Add to PATH" during installation
4. Restart your computer after installation

### Step 2: Download the Project
1. Open **Anaconda Prompt** (or **Miniconda Prompt**) from the Start menu
   - On Windows: Search for "Anaconda Prompt" or "Miniconda Prompt"
   - On Mac/Linux: Open Terminal
2. Navigate to your Desktop (or where you want to have the project):

3. Download the project:
```bash
git clone https://github.com/naderjawary/meeting-summarization-webapp.git
```
4. Navigate to the project:
```bash
cd meeting-summarization-webapp/backend
```

### Step 3: Setup the Environment
**Make sure you're still in the Anaconda/Miniconda Prompt!**
Type these commands one by one:

```bash
# Go back to main project folder
cd ..

# Create Python environment
conda create -n whisperx python=3.10 -y

# Activate environment  
conda activate whisperx

# Install FFmpeg first (required for audio processing)
conda install ffmpeg -c conda-forge -y

# Go to backend folder
cd backend

# Install Python packages
pip install -r requirements.txt
```

### Step 4: Run the Application
**Keep using the same Anaconda/Miniconda Prompt where (whisperx) appears:**
```bash
# Make sure you're in backend folder and see (whisperx) in your prompt
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Step 5: Use the Application
1. Open your web browser
2. Go to: **http://localhost:5000**
3. Upload an audio file (.mp3, .wav, etc.)
4. Click "Upload and Transcribe"
5. Wait for transcription (first time takes longer - downloads AI models)
6. Click "Generate Summary" 
7. Download PDF if needed

## Quick Start Summary

1. **Install Miniconda** → Restart computer
2. **Open Anaconda Prompt** → Navigate to Desktop
3. **Clone repository** → `git clone [repo-url]`
4. **Create environment** → `conda create -n whisperx python=3.10 -y`
5. **Activate environment** → `conda activate whisperx`
6. **Install FFmpeg** → `conda install ffmpeg -c conda-forge -y`
7. **Install packages** → `pip install -r requirements.txt`
8. **Run application** → `python app.py`
9. **Open browser** → Go to `http://localhost:5000`
10. **Test with audio file**
