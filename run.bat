@echo off
echo 🚀 Starting Local AI Chatbot...

docker compose up -d --build

echo ⏳ Waiting for Ollama...
timeout /t 5 /nobreak > nul

echo 📥 Pulling model...
docker exec ollama ollama pull llama3.2

echo ✅ Ready!
echo 👉 API: http://localhost:7070
echo 👉 UI: Open ui/index.html
pause
