# 🎥 Video Transcriptor

## 📖 Overview
Video Transcriptor is an AI-powered API application designed to generate blog posts and video transcripts in any required language. Built with an agentic architecture, this tool leverages large language models (via LangChain and LangGraph) to automate transcription, translation, and content generation. 

It provides endpoints to either generate a blog post directly from a topic or extract audio from a YouTube video, transcribe it, and convert it into a comprehensive article.

## ✨ Features
- **🎙️ Video Transcription & Processing**: Automatically downloads YouTube video audio (via `yt-dlp` and `ffmpeg`) and transcribes it using Groq's Whisper model.
- **🌍 Multilingual Support**: Generate transcripts and blog posts in the user's preferred language.
- **✍️ Blog Generation**: Convert video transcripts or standalone topics into well-structured, engaging blog posts.
- **🤖 Agentic Workflows**: Utilizes LangChain and LangGraph to manage complex, multi-step autonomous tasks (e.g., fetching video data, transcribing, writing, reviewing, and translating).
- **🔌 REST API Interface**: Easy-to-use FastAPI backend exposing `/blog` and `/videotranscript` endpoints.

## 🛠️ Technologies
- **🧠 Core AI**: LangChain, LangGraph
- **⚡ LLM Providers**: Groq (Llama models for chat, Whisper for transcription)
- **🚀 API & Backend**: FastAPI, Uvicorn
- **🎬 Media Processing**: `yt-dlp`, `ffmpeg-python`

## ⚙️ Setup & Installation

Ensure you have Python 3.12+ installed, as well as `ffmpeg` installed on your system.

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or install from the `pyproject.toml` using your preferred package manager (e.g., pip, poetry, uv).
3. Set up your environment variables by adding your API keys to the `.env` file (e.g., `GROQ_API_KEY`, `LANGSMITH_API_KEY`).

## 🚀 Usage

Start the FastAPI application using Uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 📡 Endpoints

1. **📝 Blog Generation**: `/blog`
   Generates a blog post based on a provided topic and language.
   ```bash
   curl -X POST http://127.0.0.1:8000/blog \
   -H "Content-Type: application/json" \
   -d '{"topic": "AI in healthcare", "language": "Spanish"}'
   ```

2. **🎞️ Video Transcription & Article Writer**: `/videotranscript`
   Takes a user prompt containing a YouTube URL and language preference, downloads the audio, transcribes it, and writes an article.
   ```bash
   curl -X POST http://127.0.0.1:8000/videotranscript \
   -H "Content-Type: application/json" \
   -d '{"user_input": "get me an article from https://www.youtube.com/watch?v=1UNIRI7tUrg in French"}'
   ```
