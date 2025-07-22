# ✍️ Ai-Proofreader-Bot

[![Author: %40coupdev](https://img.shields.io/badge/author-coupdev-blue)](https://coupdev.com)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A Telegram inline bot that automatically corrects grammar and punctuation using OpenAI's GPT API (GPT-3.5-turbo). Just type your text in any chat using the bot inline — it returns a corrected version instantly.

> **Example:**  
> `@YourBotUsername I has went to school`  
> ➜ `I went to school.` ✅

---

## 🚀 Features

- ✨ Fast inline grammar correction  
- 💡 Powered by OpenAI GPT-3.5-turbo  
- 🌐 Works in any chat, group, or channel (inline)  
- 🔒 No user data is stored  
- 🧠 Smart punctuation and grammar improvements

---

## 📸 Preview

| Input | Output |
|------|--------|
| `@YourBotUsername i dont know what is happaning` | `I don't know what is happening.` |
| `@YourBotUsername он пошёл в магазин но забыл купить хлеб` | `Он пошёл в магазин, но забыл купить хлеб.` |

---

## 🧰 Tech Stack

- **Python 3.10+**
- [Aiogram 3](https://github.com/aiogram/aiogram) — Telegram bot framework
- [OpenAI API](https://platform.openai.com/docs) — GPT-3.5 model
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment management

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/coupdev/Ai-Proofreader-Bot.git
cd Ai-Proofreader-Bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a .env file based on the example:

```bash
cp .env.example .env
```

Edit .env and add your credentials:

```bash
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run the bot

```bash
python bot.py
```
