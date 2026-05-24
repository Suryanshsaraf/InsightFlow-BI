# Groq API Configuration Guide

InsightFlow utilizes Groq's high-speed Llama models for instant business intelligence operations.

## Configuration Steps
1. Get a Groq API Key from the Groq console.
2. Edit your `backend/.env` file.
3. Configure settings:
   ```ini
   OPENAI_API_KEY=gsk_your_key
   OPENAI_BASE_URL=https://api.groq.com/openai/v1
   OPENAI_MODEL=llama-3.3-70b-versatile
   ```
