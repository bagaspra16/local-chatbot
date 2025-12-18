# ['name-your-own-ai-chatbot'] Assistant - Local AI Chatbot

This is a powerful, locally-hosted AI assistant powered by **Llama 3.2**. It features a modern user interface and a high-performance backend that supports real-time streaming responses.

![Local AI Chatbot](https://img.shields.io/badge/Model-Llama_3.2-blue)
![Technology](https://img.shields.io/badge/Powered%20By-Ollama-orange)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Infrastructure](https://img.shields.io/badge/Platform-Docker-blue)

## Features

- **Local Inference**: Total privacy. Your data never leaves your machine.
- **Streaming Responses**: Real-time "typewriter" effect using Server-Sent Events (SSE).
- **Llama 3.2 Powered**: High-quality responses from the latest Meta model.
- **Modern UI**: Responsive design with Dark/Light mode support and beautiful gradients.
- **Markdown Support**: Full rendering of code blocks, tables, and lists.
- **Developer Ready**: Syntax highlighting for all major programming languages.

---

## Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- [Python 3.11+](https://www.python.org/downloads/) (Optional, for local api development).

### 2. Universal Setup
We provide powerful automation scripts (`chatbot` for macOS/Linux, `run.bat` for Windows) to manage everything.

First, initialize the services:
- **macOS/Linux**: `./chatbot on`
- **Windows**: `run.bat on`

Then, download the required AI model (only needed once):
- **macOS/Linux**: `./chatbot setup`
- **Windows**: `run.bat setup`

### 3. Start Chatting
Launch the interface in your browser:
- **macOS/Linux**: `./chatbot ui`
- **Windows**: `run.bat ui`

---

## CLI Commands

The `chatbot` script is your primary control center:

### Available Commands

| Purpose | macOS / Linux | Windows (CMD/PS) | Description |
| :--- | :--- | :--- | :--- |
| **Start** | `./chatbot on` | `run.bat on` | Build and start all services in detached mode. |
| **Stop** | `./chatbot off` | `run.bat off` | Stop services and remove containers/networks. |
| **Model Setup** | `./chatbot setup` | `run.bat setup` | Download the Llama 3.2 model to the Ollama container. |
| **Open UI** | `./chatbot ui` | `run.bat ui` | Open the chat interface automatically in your browser. |
| **Monitor** | `./chatbot logs` | `run.bat logs` | Follow real-time streaming logs from the AI backend. |
| **Check** | `./chatbot status` | `run.bat status` | Inspect the health and status of active containers. |
| **Restart** | `./chatbot restart` | `run.bat restart` | Quickly restart all active services. |

> [!TIP]
> **Global Access**: To run `chatbot` from any folder, run:  
> `sudo ln -sf "$(pwd)/chatbot" /usr/local/bin/chatbot`

---

## Customization

### Themes & Colors

```css
:root {
    --primary-color: #1a45d2; /* Main Brand Color */
    --gradient-start: #0c58bb;
    --gradient-end: #300ec7;
}
```

---

## Project Structure

```text
.
├── api/                # Backend layer
│   ├── main.py         # FastAPI application logic
│   ├── Dockerfile      # API container configuration
│   └── requirements.txt
├── ui/                 # Frontend layer
│   └── index.html      # Responsive chat interface
├── chatbot             # Automation shell script
├── docker-compose.yml  # Container orchestration
└── README.md           # This file
```

---

## Security & Privacy
This application runs entirely on your local infrastructure. No data is transmitted to external servers. Your conversations remain strictly private within your Docker environment.

---
