# ✍️ Ai-Proofreader-Bot

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
