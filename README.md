# ✍️ Ai-Proofreader-Bot

<div align="center">
<p>
<a href="https://github.com/coupdev/Ai-Proofreader-Bot/">
  <img src="https://img.shields.io/badge/Author-Coupdev-89b4fa?style=for-the-badge&logo=github&logoColor=white&labelColor=302D41" alt="Author">
</a>&nbsp;&nbsp;
<a href="https://github.com/coupdev/Ai-Proofreader-Bot/blob/main/LICENSE">
  <img src="https://img.shields.io/github/license/coupdev/Ai-Proofreader-Bot?style=for-the-badge&logo=opensourceinitiative&color=CBA6F7&logoColor=CBA6F7&labelColor=302D41" alt="License">
</a>&nbsp;&nbsp;
<a href="https://github.com/coupdev/Ai-Proofreader-Bot/">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=yellow&labelColor=302D41" alt="Python">
</a>&nbsp;&nbsp;
<a href="https://github.com/coupdev/Ai-Proofreader-Bot/">
  <img src="https://img.shields.io/badge/Aiogram-3-4DABF7?style=for-the-badge&logo=telegram&logoColor=white&labelColor=302D41" alt="Aiogram">
</a>&nbsp;&nbsp;
<a href="https://github.com/coupdev/Ai-Proofreader-Bot/">
  <img src="https://img.shields.io/github/repo-size/coupdev/Ai-Proofreader-Bot?style=for-the-badge&logo=database&logoColor=f9e2af&label=Size&labelColor=302D41&color=f9e2af" alt="Repo Size">
</a>
</p>
</div>

A Telegram bot that corrects text, translates, and calculates. Works in private chat and inline. Powered by OpenRouter

---

## 🚀 Features

* ✨ Inline grammar correction (multi-language)
* 🌍 Translator: `/translate <lang?> <text>` and inline `... to <language>`
* ➗ Calculator (non‑AI): `/calc <expression>` and inline `/calc <expression>`
* 💡 Powered by OpenRouter
* 🌐 Works in any chat (inline) and in private messages
* 🔒 No user data is stored

---

## 📸 Preview

| Input                                                    | Output                                    |
| -------------------------------------------------------- | ----------------------------------------- |
| @YourBotUsername i dont know what is happaning           | I don't know what is happening.           |
| @YourBotUsername он пошёл в магазин но забыл купить хлеб | Он пошёл в магазин, но забыл купить хлеб. |

---

## 🧰 Tech Stack

* **Python 3.10+**
* Aiogram 3 — Telegram bot framework
* OpenRouter — Grok 4 Fast (Free)
* aiohttp — HTTP client for API requests
* python-dotenv — Environment management

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

```
BOT_TOKEN=your_token
OPENROUTE_API_KEY=your_api_key
```

### 4. Run the bot

#### Direct Python
```bash
python bot.py
```

## 💬 Usage

### Inline (works in any chat)

- Correction: type `@YourBotUsername <text>`
- Translate: type `@YourBotUsername <text> to <language>`
- Calculate: type `@YourBotUsername /calc <expression>`

Examples:

```text
@YourBotUsername i has went to school
→ I went to school.

@YourBotUsername Привет как дела to English
→ Hi, how are you?

@YourBotUsername /calc (10+5)*2%
→ 0.3
```

### Private chat commands

- `/translate <lang?> <text>` — translates corrected text; defaults to English if `<lang>` omitted
- `/calc <expression>` — local calculator, supports `+ - * / () %`; replies with number only
