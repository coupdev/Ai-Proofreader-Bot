# Импорты / Imports
import asyncio
import logging
import os
from typing import Optional, Tuple
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from dotenv import load_dotenv

# Загрузка переменных окружения / Load environment variables
load_dotenv()

# Настройка логирования / Logging configuration
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера / Initialize bot and dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Конфигурация OpenRouter / OpenRouter configuration
# Предпочитать OPENROUTER_API_KEY, поддерживать устаревший OPENROUTE_API_KEY / Prefer OPENROUTER_API_KEY, support legacy OPENROUTE_API_KEY
OPENROUTE_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTE_API_KEY")
OPENROUTE_URL = "https://openrouter.ai/api/v1/chat/completions"
# Идентификатор модели / Model identifier 
PRIMARY_MODEL_ID = os.getenv("MODEL_ID", "deepseek/deepseek-chat-v3.1:free")


async def correct_text(text: str) -> Optional[str]:
    """
    Исправление грамматики и пунктуации через OpenRouter API / Correct grammar and punctuation using OpenRouter API
    """
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTE_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/coupdev/Ai-Proofreader-Bot",
            "X-Title": "AI Proofreader Bot"
        }
        
        # Системный промпт для коррекции / System prompt for correction
        system_prompt = """You are an expert multi-language grammar, slang, and profanity correction assistant.  
Your task is to return the corrected version of the input text while fully respecting its style and vocabulary.  

Rules:  
1. Correct grammar, spelling, punctuation, syntax, and word forms.  
2. Never censor or remove slang, street talk, dialects, or profanity.  
3. Support Russian, English, and all other languages the model knows — including mixed-language sentences (code-switching).  
4. If the text contains strong or vulgar language (мат, curse words, offensive slang), preserve it, only fix grammar and flow.  
5. Respect style:  
   - Informal text stays informal.  
   - Street slang, gaming slang, memes, profanity — all remain intact.  
   - Formal/neutral text stays formal/neutral.  
6. If the text is already correct, return it unchanged.  
7. Output only the corrected text — no explanations, no comments.  
8. Always preserve the emotional tone and energy of the original (whether it’s chill, angry, funny, aggressive, romantic, etc.).  

Examples:  
- "i has went to school" → "I went to school."  
- "он пошёл в магазин но забыл купить хлеб" → "Он пошёл в магазин, но забыл купить хлеб."  
- "ща пойду в shop куплю new sneakers" → "Ща пойду в shop, куплю new sneakers."  
- "бля я заебался работать нахуй" → "Бля, я заебался работать, нахуй."  
- "this shit is fckn awesome" → "This shit is fuckin' awesome."  
- "нах мне этот meeting если я и так busy" → "Нах мне этот meeting, если я и так busy."""

        payload = {
            "model": PRIMARY_MODEL_ID,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        # Вызов OpenRouter Chat Completions / Call OpenRouter Chat Completions
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTE_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    corrected_text = result["choices"][0]["message"]["content"].strip()
                    logger.info(f"Successfully corrected text")
                    return corrected_text
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRoute API error: {response.status} - {error_text}")
                    # 404: эндпоинт недоступен для текущей модели / 404: no endpoints for current model
                    # Повтор при 429 (лимит) один раз / Retry once on 429 rate limit
                    if response.status == 429:
                        try:
                            await asyncio.sleep(0.6)
                            async with session.post(OPENROUTE_URL, headers=headers, json=payload) as retry_resp:
                                if retry_resp.status == 200:
                                    result_r = await retry_resp.json()
                                    corrected_retry = result_r["choices"][0]["message"]["content"].strip()
                                    logger.info("Successfully corrected text after retry")
                                    return corrected_retry
                        except Exception as _:
                            pass
                    # Без фолбэка: вернуть None / No fallback; surface error
                    return None
    
    except Exception as e:
        logger.error(f"Error correcting text: {e}")
        return None

async def translate_text(text: str, target_language: Optional[str]) -> Optional[str]:
    """
    Перевод текста через OpenRouter API (по умолчанию на английский при None) / Translate text via OpenRouter API (defaults to English when None)
    Возвращает только перевод без комментариев / Returns only translated text, no commentary
    """
    try:
        def normalize_language_name(raw: Optional[str]) -> str:
            """
            Map common ISO codes and aliases to canonical English language names.
            Defaults to "English" when input is None/empty/unknown.
            """
            if not raw:
                return "English"
            alias = raw.strip().lower()
            mapping = {
                # English
                "en": "English", "eng": "English", "english": "English",
                # Russian
                "ru": "Russian", "rus": "Russian", "russian": "Russian", "рус": "Russian", "русский": "Russian",
                # Ukrainian
                "uk": "Ukrainian", "ua": "Ukrainian", "ukrainian": "Ukrainian", "украинский": "Ukrainian",
                # German
                "de": "German", "ger": "German", "deu": "German", "german": "German", "нем": "German", "немецкий": "German",
                # French
                "fr": "French", "fra": "French", "fre": "French", "french": "French", "французский": "French",
                # Spanish
                "es": "Spanish", "spa": "Spanish", "spanish": "Spanish", "испанский": "Spanish",
                # Italian
                "it": "Italian", "ita": "Italian", "italian": "Italian", "итальянский": "Italian",
                # Portuguese
                "pt": "Portuguese", "por": "Portuguese", "portuguese": "Portuguese", "португальский": "Portuguese",
                # Chinese
                "zh": "Chinese", "cmn": "Chinese", "chinese": "Chinese", "中文": "Chinese", "китайский": "Chinese",
                # Japanese
                "ja": "Japanese", "jpn": "Japanese", "japanese": "Japanese", "японский": "Japanese",
                # Korean
                "ko": "Korean", "kor": "Korean", "korean": "Korean", "корейский": "Korean",
                # Turkish
                "tr": "Turkish", "tur": "Turkish", "turkish": "Turkish", "турецкий": "Turkish",
                # Arabic
                "ar": "Arabic", "ara": "Arabic", "arabic": "Arabic", "арабский": "Arabic",
                # Polish
                "pl": "Polish", "pol": "Polish", "polish": "Polish", "польский": "Polish",
            }
            return mapping.get(alias, raw.strip().title())

        def _strip_quotes(s: str) -> str:
            if not s:
                return s
            t = s.strip()
            if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                return t[1:-1].strip()
            return t
        headers = {
            "Authorization": f"Bearer {OPENROUTE_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/coupdev/Ai-Proofreader-Bot",
            "X-Title": "AI Proofreader Bot"
        }

        target = normalize_language_name(target_language)

        system_prompt = (
            "You are a precise translation assistant. Translate the user's message into the target language.\n"
            "Rules:\n"
            "1) Output ONLY the translation, no quotes, no comments.\n"
            "2) Preserve tone, style, slang, and profanity.\n"
            "3) Keep names and proper nouns intact.\n"
            "Target language: " + target
        )

        payload = {
            "model": PRIMARY_MODEL_ID,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "max_tokens": 1000,
            "temperature": 0.2,
            "top_p": 0.9
        }

        # Вызов OpenRouter Chat Completions / Call OpenRouter Chat Completions
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTE_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    translated = _strip_quotes(result["choices"][0]["message"]["content"]) 
                    logger.info("Successfully translated text")
                    return translated
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRoute API error (translate): {response.status} - {error_text}")
                    # 404: эндпоинт недоступен для текущей модели / 404: no endpoints for current model
                    if response.status == 429:
                        try:
                            await asyncio.sleep(0.6)
                            async with session.post(OPENROUTE_URL, headers=headers, json=payload) as retry_resp:
                                if retry_resp.status == 200:
                                    result_r = await retry_resp.json()
                                    translated_r = _strip_quotes(result_r["choices"][0]["message"]["content"]) 
                                    logger.info("Successfully translated after retry")
                                    return translated_r
                        except Exception as _:
                            pass
                    # Без фолбэка: вернуть None / No fallback; surface error
                    return None
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return None

def _preprocess_percentages(expr: str) -> str:
    """
    Заменяет 50% на (50/100); сохраняет остальные операторы и скобки / Replace 50% with (50/100); keep others
    """
    import re
    def repl(m: re.Match) -> str:
        number = m.group(1)
        return f"({number}/100)"
    return re.sub(r"(?<![A-Za-z_])((?:\d+\.\d+)|(?:\d+))%", repl, expr)

def _safe_eval(expression: str) -> float:
    """
    Безопасная оценка выражения с поддержкой +, -, *, /, скобок и процентов / Safe eval
    """
    import ast
    import operator as op

    operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.USub: op.neg,
        ast.UAdd: op.pos,
    }

    def eval_node(node: ast.AST) -> float:
        if isinstance(node, ast.Num):
            return float(node.n)
        if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
            return operators[type(node.op)](eval_node(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
            left = eval_node(node.left)
            right = eval_node(node.right)
            return operators[type(node.op)](left, right)
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Unsupported expression")

    cleaned = _preprocess_percentages(expression.replace(",", "."))
    tree = ast.parse(cleaned, mode="eval")
    return eval_node(tree.body)

def parse_inline_translate_query(query: str) -> Optional[Tuple[str, Optional[str]]]:
    """
    Разбор inline-запроса: "text to German" или "/translate German text" / Inline parse
    Возвращает (текст, язык|None). None → перевод на английский / Returns (text, lang|None)
    """
    q = query.strip()
    if not q:
        return None
    lower_q = q.lower()
    if lower_q.startswith("/translate") or lower_q.startswith("translate ") or lower_q.startswith("trans ") or lower_q.startswith("bkb "):
        parts = q.split(maxsplit=2)
        # /translate <lang> <text>  OR  /translate <text>
        if len(parts) == 1:
            return None
        if len(parts) == 2:
            # If user provided only one token after command, detect if it's likely a language
            token = parts[1].strip()
            # Heuristic: short or known aliases -> treat as language without text (invalid)
            if token.lower() in {"en","eng","english","ru","rus","russian","de","german","fr","french","es","spanish","it","italian","pt","portuguese"} or len(token) <= 3:
                return None
            # Otherwise assume it's text, default to English
            return (parts[1], None)
        # len == 3, assume parts[1] is language
        lang = parts[1].strip()
        txt = parts[2].strip()
        if not txt:
            return None
        return (txt, lang)
    # Шаблон: ... to <language> / Pattern
    lower = lower_q
    # Support "text -> lang" pattern
    if "->" in q:
        idx = q.rfind("->")
        text = q[:idx].strip()
        lang = q[idx+2:].strip()
        if text and lang:
            return (text, lang)
    # Поддержка: "to: lang" и "to lang" / Support
    if " to:" in lower:
        idx = lower.rfind(" to:")
        text = q[:idx].strip()
        lang = q[idx+4:].strip(" :")
        if text and lang:
            return (text, lang)
    sep = " to "
    if sep in lower:
        idx = lower.rfind(sep)
        text = q[:idx].strip()
        lang = q[idx+len(sep):].strip()
        if text and lang:
            return (text, lang)
    # Шаблон: lang: text (напр., "english: Привет") / Pattern
    if ":" in q:
        lang, maybe_text = q.split(":", 1)
        lang = lang.strip()
        maybe_text = maybe_text.strip()
        if lang and maybe_text and len(lang) <= 20:
            return (maybe_text, lang)
    return None


@dp.inline_query()
async def inline_handler(inline_query: InlineQuery):
    """
    Обработка inline-запросов: коррекция, перевод, калькулятор / Handle inline queries
    """
    query = inline_query.query.strip()
    
    if not query:
        # Show function suggestions when user just types @Bot
        suggestion_correct = InlineQueryResultArticle(
            id="sugg-correct",
            title="Correct text / Исправление текста",
            description="Type your text to get corrected version",
            input_message_content=InputTextMessageContent(
                message_text="Type @BotUsername <your text> to get corrected version"
            ),
            thumb_url="https://files.catbox.moe/4559um.jpeg"
        )
        suggestion_translate = InlineQueryResultArticle(
            id="sugg-translate",
            title="Translate / Перевод",
            description="Examples: trans en Привет | Hello to Russian | english: Привет",
            input_message_content=InputTextMessageContent(
                message_text="Example: trans en Привет -> Hello"
            ),
            thumb_url="https://files.catbox.moe/5l00tv.jpeg"
        )
        suggestion_calc = InlineQueryResultArticle(
            id="sugg-calc",
            title="Calculator / Калькулятор",
            description="Example: calc (10+5)*2% → 0.3",
            input_message_content=InputTextMessageContent(
                message_text="calc (10+5)*2%"
            ),
            thumb_url="https://files.catbox.moe/dwu5lb.jpeg"

        )
        await inline_query.answer([suggestion_correct, suggestion_translate, suggestion_calc], cache_time=1, is_personal=True)
        return
    
    # Inline калькулятор: /calc <expr> или calc <expr> / Inline calculator
    ql = query.lstrip()
    lower = ql.lower()
    if lower.startswith("/calc") or lower.startswith("calc") or lower.startswith("calculate"):
        parts = ql.split(maxsplit=1)
        if len(parts) == 1:
            # Only show calculator suggestion (single option)
            suggestion_calc = InlineQueryResultArticle(
                id="sugg-calc",
                title="Calculator / Калькулятор",
                description="Example: calc (10+5)*2% -> 0.3",
                input_message_content=InputTextMessageContent(
                    message_text="calc (10+5)*2%"
                ),
                thumb_url="https://files.catbox.moe/dwu5lb.jpeg"
            )
            await inline_query.answer([suggestion_calc], cache_time=1, is_personal=True)
            return
        expr = parts[1]
        try:
            value = _safe_eval(expr)
            result = InlineQueryResultArticle(
                id="calc-1",
                title=str(value),
                description=str(value),
                input_message_content=InputTextMessageContent(message_text=str(value))
            )
            await inline_query.answer([result], cache_time=1)
            return
        except Exception:
            await inline_query.answer([], cache_time=1)
            return

    # Inline перевод: алиасы (trans, translate, bkb), паттерны (text to <lang>, ->, to:) / Inline translate
    # If user typed only translate aliases without args, show only translate suggestion
    if lower.startswith("/translate") or lower.startswith("translate") or lower.startswith("trans") or lower.startswith("bkb"):
        tokens = ql.split(maxsplit=1)
        if len(tokens) == 1:
            suggestion_translate = InlineQueryResultArticle(
                id="sugg-translate",
                title="Translate / Перевод",
                description="Examples: trans en Привет | Hello to Russian | english: Привет",
                input_message_content=InputTextMessageContent(
                    message_text="Example: trans en Привет -> Hello"
                ),
                thumb_url="https://files.catbox.moe/5l00tv.jpeg"
            )
            await inline_query.answer([suggestion_translate], cache_time=1, is_personal=True)
            return

    parsed = parse_inline_translate_query(query)
    if parsed:
        text, lang = parsed
        # Try translation on corrected text first; if translation fails, try raw text once
        corrected = await correct_text(text)
        source = corrected if corrected else text
        translated = await translate_text(source, lang)
        if not translated and corrected:
            translated = await translate_text(text, lang)
        if translated:
            result = InlineQueryResultArticle(
                id="tr-1",
                title="Translation/Перевод",
                description=translated,
                input_message_content=InputTextMessageContent(message_text=translated),
                thumb_url="https://files.catbox.moe/5l00tv.jpeg"
            )
            await inline_query.answer([result], cache_time=1)
            return
        await inline_query.answer([], cache_time=1)
        return

    # По умолчанию: исправление текста / Default: correct the text
    corrected_text = await correct_text(query)
    
    if corrected_text and corrected_text != query:
        result = InlineQueryResultArticle(
            id="1",
            title="Corrected Text/Исправленный Текст",
            description=corrected_text,
            input_message_content=InputTextMessageContent(
                message_text=corrected_text
            ),
            thumb_url="https://files.catbox.moe/4559um.jpeg"
        )
        await inline_query.answer([result], cache_time=1)
    else:
        result = InlineQueryResultArticle(
            id="1",
            title="No corrections needed",
            description="The text appears to be correct or couldn't be processed",
            input_message_content=InputTextMessageContent(
                message_text=query
            ),
            thumb_url="https://files.catbox.moe/4559um.jpeg"
        )
        await inline_query.answer([result], cache_time=1)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    """
    Обработка команды /start / Handle /start command
    """
    await message.answer(
        "👋 Hi there! I'm AI Proofreader Bot 🤖\n\n"
        "I can help you:\n"
        "✨ Correct text mistakes\n"
        "🌍 Translate into different languages\n"
        "🧮 Calculate expressions right in the chat\n\n"
        "How to use:\n"
        "• Just type:\n"
        "@AiProofreaderBot i has went to school -> I went to school.\n"
        "• To translate:\n"
        "@AiProofreaderBot Привет как дела to English -> Hi, how are you?\n"
        "• To calculate:\n"
        "@AiProofreaderBot /calc 2+2*2 -> 6\n\n"
        "Commands:\n"
        "🔹 /translate <language> <text> — translate text (default: English)\n"
        "🔹 /calc <expression> — calculator (+, -, *, /, %, parentheses)\n\n"
        "🚀 Try it out now!\n\n"
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    """
    Обработка команды /help / Handle /help command
    """
    await message.answer(
        "📖 Help\n\n"
        "This bot can correct text, translate, and calculate.\n\n"
        "Commands:\n"
        "/translate <lang> <text> - translate corrected text (default to English)\n"
        "/calc <expression> - calculator ( +|-|*|/|()|% )\n\n"
        "Inline:\n"
        "- Correction: @AiProofreaderBot <text>\n"
        "- Translate: @AiProofreaderBot <text> to <language>\n"
        "- Calculate: @AiProofreaderBot calc <expression>"
    )


@dp.message(Command("translate"))
async def translate_command(message: types.Message):
    """
    Обработка /translate <lang?> <text> (личные и группы) / Handle /translate
    """
    text = message.text or ""
    parts = text.split(maxsplit=2)
    if len(parts) == 1:
        await message.answer("Usage: /translate <lang?> <text>")
        return
    if len(parts) == 2:
        # No language specified, translate to English
        src_text = parts[1]
        lang = None
    else:
        lang = parts[1]
        src_text = parts[2]

    # Try translation on corrected text first; if translation fails, try raw text once
    corrected = await correct_text(src_text)
    source = corrected if corrected else src_text
    translated = await translate_text(source, lang)
    if not translated and corrected:
        translated = await translate_text(src_text, lang)
    if translated:
        await message.answer(translated)
    else:
        await message.answer("Translation failed. Try again later.")


@dp.message(Command("calc"))
async def calc_command(message: types.Message):
    """
    Обработка /calc <expression> (локальный калькулятор); отвечает числом / Handle /calc
    """
    text = message.text or ""
    expr = text[5:].strip()
    if not expr:
        await message.answer("0")
        return
    try:
        value = _safe_eval(expr)
        await message.answer(str(value))
    except Exception:
        # On error, don't send AI text, reply minimal numeric fallback
        await message.answer("0")


async def main():
    """
    Точка входа: запуск бота / Main function to start the bot
    """
    try:
        # Проверка обязательных переменных окружения / Check required environment variables
        if not os.getenv("BOT_TOKEN"):
            logger.error("BOT_TOKEN not found in environment variables")
            return
        
        if not OPENROUTE_API_KEY:
            logger.error("OPENROUTER_API_KEY not found in environment variables")
            return
        
        logger.info("Starting AI Proofreader Bot...")
        
        # Удаление вебхука для избежания конфликтов с polling / Ensure webhook is removed before polling
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass

        # Запуск polling / Start polling
        await dp.start_polling(bot)
    
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())