@echo off
setlocal enabledelayedexpansion

set CMD=%1

if "%CMD%"=="" goto help
if "%CMD%"=="on" goto on
if "%CMD%"=="off" goto off
if "%CMD%"=="restart" goto restart
if "%CMD%"=="status" goto status
if "%CMD%"=="setup" goto setup
if "%CMD%"=="logs" goto logs
if "%CMD%"=="ui" goto ui

:on
echo 🚀 Starting Chatbot Services...
docker compose up -d --build
goto end

:off
echo 🛑 Stopping Chatbot Services...
docker compose down
goto end

:restart
echo 🔄 Restarting Chatbot Services...
docker compose restart
goto end

:status
docker compose ps
goto end

:setup
echo 📥 Pulling Llama 3.2 model...
docker exec -it ollama ollama pull llama3.2
echo ✅ Setup complete.
goto end

:logs
docker compose logs -f
goto end

:ui
echo 🌐 Opening UI in browser...
start ui\index.html
goto end

:help
echo Usage: run.bat [command]
echo.
echo Commands:
echo   on       Start all services
echo   off      Stop and remove containers
echo   restart  Restart services
echo   status   Check service status
echo   setup    Download/pull the required AI model
echo   logs     View real-time logs
echo   ui       Open the chat interface in browser
goto end

:end
pause
