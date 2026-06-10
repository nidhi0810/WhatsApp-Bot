# WhatsApp AI Bot

A lightweight AI-powered WhatsApp bot built using Baileys and OpenRouter.

Unlike the official WhatsApp Business API, this bot works through WhatsApp Web, making it free to use for personal projects, learning, and hackathons. There are no per-message API charges from WhatsApp, and it can respond to messages in real time using any LLM available through OpenRouter.

## Features

* Free WhatsApp integration using Baileys
* No Twilio required
* No WhatsApp Business API required
* AI-powered responses via OpenRouter
* QR-code authentication
* Session persistence
* Easy to extend with tools and agents

## Tech Stack

* Node.js
* Baileys
* OpenRouter
* OpenAI SDK
* dotenv

## Run

```bash
npm install
node index.js
```

Scan the QR code using WhatsApp Linked Devices and start chatting with your AI assistant.
