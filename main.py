# main.py
import asyncio
import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, InlineQueryHandler, ContextTypes
import aiosqlite

# ---------- Bot config ----------
BOT_TOKEN = "8264679566:AAFpbMd_g6Tbv3GfShREtCM0CW078ujPixY"
BOT_USERNAME = "@inline_text_maker_bot"

# ---------- Database ----------
DB_PATH = "bot_data.db"

# ---------- Language strings ----------
STRINGS = {
    "en": {
        "start": "Welcome! I'm Inline Text Maker 💠\nYou can create custom inline button posts and share them anywhere.",
        "create_btn": "🔗 Create Inline Link",
        "my_posts_btn": "📁 My Posts",
        "language_btn": "🌐 Change Language",
        "developer_btn": "👨‍💻 Developer",
        "update_channel_btn": "📢 Update Channel",
        "send_format": "Send your post in this format:\n`Text | Link | Color_emoji`\nExample: `My Site | https://example.com | 🔴`\n(Color emoji is optional, default 🔵)",
        "invalid_format": "❌ Invalid format! Please use `Text | Link | [Emoji]`.",
        "post_created": "✅ Post created!\n📌 Code: `{code}`\n\nUsage: Type @inline_text_maker_bot {code} in any chat.",
        "no_posts": "You have no posts yet.",
        "post_deleted": "❌ Post deleted.",
        "edit_prompt": "Send new data in format (`Text | Link | [Emoji]`)",
        "post_updated": "✏️ Post updated.",
        "cancel": "Cancel",
        "done": "Done",
        "language_selected": "Language set to English.",
        "inline_help": "Type @inline_text_maker_bot <code> or leave empty to see your posts.",
        "unauthorized": "❌ You can't modify this post.",
        "post_not_found": "Post not found.",
        "choose_lang": "Choose language:",
        "cancel_text": "Action cancelled.",
        "back_to_menu": "Back to menu."
    },
    "bn": {
        "start": "স্বাগতম! আমি ইনলাইন টেক্সট মেকার বট 💠\nআপনি নিজের কাস্টম ইনলাইন বাটন পোস্ট তৈরি করে যেকোনো চ্যাটে শেয়ার করতে পারবেন।",
        "create_btn": "🔗 ইনলাইন লিংক তৈরি করুন",
        "my_posts_btn": "📁 আমার পোস্টসমূহ",
        "language_btn": "🌐 ভাষা পরিবর্তন করুন",
        "developer_btn": "👨‍💻 ডেভেলপার",
        "update_channel_btn": "📢 আপডেট চ্যানেল",
        "send_format": "পোস্ট তৈরির জন্য এই ফরম্যাটে মেসেজ পাঠান:\n`টেক্সট | লিংক | কালার ইমোজি`\nউদাহরণ: `আমার সাইট | https://example.com | 🔴`\n(কালার ইমোজি অপশনাল, না দিলে নীল হবে)",
        "invalid_format": "❌ ফরম্যাট সঠিক নয়! দয়া করে `টেক্সট | লিংক | [ইমোজি]` ফরম্যাটে পাঠান।",
        "post_created": "✅ পোস্ট তৈরি হয়েছে!\n📌 কোড: `{code}`\n\nব্যবহার: যেকোনো চ্যাটে @inline_text_maker_bot {code} লিখে পাঠান।",
        "no_posts": "আপাতত আপনার কোনো পোস্ট নেই।",
        "post_deleted": "❌ পোস্ট ডিলিট করা হয়েছে।",
        "edit_prompt": "এখন নতুন তথ্য ফরম্যাটে পাঠান (`টেক্সট | লিংক | [ইমোজি]`)",
        "post_updated": "✏️ পোস্ট আপডেট হয়েছে।",
        "cancel": "বাতিল",
        "done": "সম্পন্ন",
        "language_selected": "ভাষা বাংলা নির্বাচিত হয়েছে।",
        "inline_help": "টাইপ করুন @inline_text_maker_bot <কোড> অথবা খালি রাখলে আপনার পোস্ট দেখতে পাবেন।",
        "unauthorized": "❌ আপনি এই পোস্ট পরিবর্তন করতে পারবেন না।",
        "post_not_found": "পোস্ট পাওয়া যায়নি।",
        "choose_lang": "ভাষা বাছাই করুন:",
        "cancel_text": "কাজ বাতিল করা হয়েছে।",
        "back_to_menu": "মেনুতে ফিরুন।"
    },
    "ru": {
        "start": "Добро пожаловать! Я Inline Text Maker 💠\nСоздавайте кастомные посты с инлайн‑кнопками и делитесь ими везде.",
        "create_btn": "🔗 Создать инлайн‑ссылку",
        "my_posts_btn": "📁 Мои посты",
        "language_btn": "🌐 Сменить язык",
        "developer_btn": "👨‍💻 Разработчик",
        "update_channel_btn": "📢 Канал обновлений",
        "send_format": "Отправьте пост в формате:\n`Текст | Ссылка | Эмодзи_цвета`\nПример: `Мой сайт | https://example.com | 🔴`\n(Цветной эмодзи необязателен, по умолчанию 🔵)",
        "invalid_format": "❌ Неверный формат! Используйте `Текст | Ссылка | [Эмодзи]`.",
        "post_created": "✅ Пост создан!\n📌 Код: `{code}`\n\nИспользование: в любом чате введите @inline_text_maker_bot {code}.",
        "no_posts": "У вас пока нет постов.",
        "post_deleted": "❌ Пост удалён.",
        "edit_prompt": "Отправьте новые данные в формате (`Текст | Ссылка | [Эмодзи]`)",
        "post_updated": "✏️ Пост обновлён.",
        "cancel": "Отмена",
        "done": "Готово",
        "language_selected": "Язык изменён на русский.",
        "inline_help": "Введите @inline_text_maker_bot <код> или оставьте пустым, чтобы увидеть свои посты.",
        "unauthorized": "❌ Вы не можете изменять этот пост.",
        "post_not_found": "Пост не найден.",
        "choose_lang": "Выберите язык:",
        "cancel_text": "Действие отменено.",
        "back_to_menu": "Вернуться в меню."
    },
    "hi": {
        "start": "स्वागत है! मैं Inline Text Maker 💠\nआप कस्टम इनलाइन बटन पोस्ट बना सकते हैं और कहीं भी शेयर कर सकते हैं।",
        "create_btn": "🔗 इनलाइन लिंक बनाएं",
        "my_posts_btn": "📁 मेरे पोस्ट",
        "language_btn": "🌐 भाषा बदलें",
        "developer_btn": "👨‍💻 डेवलपर",
        "update_channel_btn": "📢 अपडेट चैनल",
        "send_format": "पोस्ट इस फॉर्मेट में भेजें:\n`टेक्स्ट | लिंक | रंग ईमोजी`\nउदाहरण: `मेरी साइट | https://example.com | 🔴`\n(रंग ईमोजी वैकल्पिक, डिफ़ॉल्ट 🔵)",
        "invalid_format": "❌ गलत फॉर्मेट! कृपया `टेक्स्ट | लिंक | [ईमोजी]` का उपयोग करें।",
        "post_created": "✅ पोस्ट बन गया!\n📌 कोड: `{code}`\n\nउपयोग: किसी भी चैट में @inline_text_maker_bot {code} लिखें।",
        "no_posts": "आपके पास अभी तक कोई पोस्ट नहीं है।",
        "post_deleted": "❌ पोस्ट हटा दिया गया।",
        "edit_prompt": "नया डेटा फॉर्मेट में भेजें (`टेक्स्ट | लिंक | [ईमोजी]`)",
        "post_updated": "✏️ पोस्ट अपडेट किया गया।",
        "cancel": "रद्द करें",
        "done": "हो गया",
        "language_selected": "भाषा हिंदी चुन ली गई है।",
        "inline_help": "टाइप करें @inline_text_maker_bot <कोड> या खाली छोड़ें अपने पोस्ट देखने के लिए।",
        "unauthorized": "❌ आप इस पोस्ट को बदल नहीं सकते।",
        "post_not_found": "पोस्ट नहीं मिला।",
        "choose_lang": "भाषा चुनें:",
        "cancel_text": "कार्रवाई रद्द कर दी गई।",
        "back_to_menu": "मेनू पर वापस जाएं।"
    }
}

# ---------- Helpers ----------
def generate_code():
    """Generate a 6‑char alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def get_db():
    """Return a database connection (create if needed)."""
    return await aiosqlite.connect(DB_PATH)

async def init_db():
    """Initialize database tables."""
    db = await get_db()
    await db.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        lang TEXT DEFAULT 'bn'
    )''')
    await db.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        code TEXT UNIQUE,
        text TEXT,
        link TEXT,
        color_emoji TEXT DEFAULT '🔵'
    )''')
    await db.commit()
    await db.close()

# ---------- Database operations ----------
async def get_user_lang(user_id):
    db = await get_db()
    cursor = await db.execute('SELECT lang FROM users WHERE user_id = ?', (user_id,))
    row = await cursor.fetchone()
    await db.close()
    return row[0] if row else 'bn'  # default Bangla

async def set_user_lang(user_id, lang):
    db = await get_db()
    await db.execute('INSERT INTO users (user_id, lang) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET lang = ?',
                     (user_id, lang, lang))
    await db.commit()
    await db.close()

async def create_post(user_id, text, link, color_emoji):
    db = await get_db()
    while True:
        code = generate_code()
        try:
            await db.execute('INSERT INTO posts (user_id, code, text, link, color_emoji) VALUES (?, ?, ?, ?, ?)',
                             (user_id, code, text, link, color_emoji))
            await db.commit()
            break
        except aiosqlite.IntegrityError:  # code collision, regenerate
            continue
    await db.close()
    return code

async def get_user_posts(user_id, limit=50):
    db = await get_db()
    cursor = await db.execute('SELECT id, code, text, link, color_emoji FROM posts WHERE user_id = ? ORDER BY id DESC LIMIT ?',
                              (user_id, limit))
    rows = await cursor.fetchall()
    await db.close()
    return [{'id': r[0], 'code': r[1], 'text': r[2], 'link': r[3], 'color_emoji': r[4]} for r in rows]

async def get_post_by_code(code):
    db = await get_db()
    cursor = await db.execute('SELECT id, user_id, text, link, color_emoji FROM posts WHERE code = ?', (code,))
    row = await cursor.fetchone()
    await db.close()
    if row:
        return {'id': row[0], 'user_id': row[1], 'text': row[2], 'link': row[3], 'color_emoji': row[4]}
    return None

async def get_post_by_id(post_id):
    db = await get_db()
    cursor = await db.execute('SELECT id, user_id, text, link, color_emoji, code FROM posts WHERE id = ?', (post_id,))
    row = await cursor.fetchone()
    await db.close()
    if row:
        return {'id': row[0], 'user_id': row[1], 'text': row[2], 'link': row[3], 'color_emoji': row[4], 'code': row[5]}
    return None

async def delete_post(post_id, user_id):
    db = await get_db()
    await db.execute('DELETE FROM posts WHERE id = ? AND user_id = ?', (post_id, user_id))
    await db.commit()
    await db.close()

async def update_post(post_id, user_id, text, link, color_emoji):
    db = await get_db()
    await db.execute('UPDATE posts SET text = ?, link = ?, color_emoji = ? WHERE id = ? AND user_id = ?',
                     (text, link, color_emoji, post_id, user_id))
    await db.commit()
    await db.close()

# ---------- State management (in memory) ----------
# user_state: {user_id: {'action': 'awaiting_post' or 'awaiting_edit', 'post_id': int} }
user_states = {}

# ---------- Keyboards ----------
def main_menu_keyboard(lang):
    s = STRINGS[lang]
    keyboard = [
        [InlineKeyboardButton(s["create_btn"], callback_data="create_post")],
        [InlineKeyboardButton(s["my_posts_btn"], callback_data="my_posts")],
        [InlineKeyboardButton(s["language_btn"], callback_data="change_lang")],
        [InlineKeyboardButton(s["developer_btn"], callback_data="developer")],
        [InlineKeyboardButton(s["update_channel_btn"], url="https://t.me/earning_channel24")]
    ]
    return InlineKeyboardMarkup(keyboard)

def cancel_keyboard(lang):
    s = STRINGS[lang]
    return InlineKeyboardMarkup([[InlineKeyboardButton(s["cancel"], callback_data="cancel_action")]])

def language_keyboard():
    buttons = [
        [InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")]
    ]
    return InlineKeyboardMarkup(buttons)

def post_actions_keyboard(post_id, lang):
    s = STRINGS[lang]
    buttons = [
        InlineKeyboardButton(s["post_deleted"].replace("❌", "🗑️"), callback_data=f"delete_{post_id}"),
        InlineKeyboardButton(s["post_updated"].split(" ")[0] + " ✏️", callback_data=f"edit_{post_id}")
    ]
    return InlineKeyboardMarkup([buttons])

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await get_user_lang(user_id)
    s = STRINGS[lang]
    await update.message.reply_text(s["start"], reply_markup=main_menu_keyboard(lang))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = await get_user_lang(user_id)
    s = STRINGS[lang]
    data = query.data

    if data == "create_post":
        user_states[user_id] = {'action': 'awaiting_post'}
        await query.edit_message_text(s["send_format"], parse_mode="Markdown", reply_markup=cancel_keyboard(lang))
    elif data == "my_posts":
        posts = await get_user_posts(user_id)
        if not posts:
            await query.edit_message_text(s["no_posts"], reply_markup=main_menu_keyboard(lang))
        else:
            text = "📁 " + ("Your posts" if lang == "en" else "আপনার পোস্ট" if lang == "bn" else "Ваши посты" if lang == "ru" else "आपके पोस्ट") + ":\n\n"
            for p in posts:
                text += f"🔹 {p['color_emoji']} {p['text']}  —  `{p['code']}`\n"
            text += "\n" + s["inline_help"]
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton(s["back_to_menu"], callback_data="back_to_menu")]
                                          ]))
    elif data == "change_lang":
        await query.edit_message_text(s["choose_lang"], reply_markup=language_keyboard())
    elif data.startswith("lang_"):
        new_lang = data.split("_")[1]
        await set_user_lang(user_id, new_lang)
        lang = new_lang
        s = STRINGS[lang]
        await query.edit_message_text(s["language_selected"], reply_markup=main_menu_keyboard(lang))
    elif data == "developer":
        dev_text = "👨‍💻 Developers:\n@Bot_developer_io & @jhgmaing"
        await query.edit_message_text(dev_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(s["back_to_menu"], callback_data="back_to_menu")]
        ]))
    elif data == "back_to_menu":
        if user_id in user_states:
            del user_states[user_id]
        await query.edit_message_text(s["start"], reply_markup=main_menu_keyboard(lang))
    elif data.startswith("delete_"):
        post_id = int(data.split("_")[1])
        # confirm deletion
        await query.edit_message_text("Delete this post? (yes/no)",
                                       reply_markup=InlineKeyboardMarkup([
                                           [InlineKeyboardButton("✅ Yes", callback_data=f"confirm_delete_{post_id}"),
                                            InlineKeyboardButton("❌ No", callback_data="my_posts")]
                                       ]))
    elif data.startswith("edit_"):
        post_id = int(data.split("_")[1])
        post = await get_post_by_id(post_id)
        if not post or post['user_id'] != user_id:
            await query.edit_message_text(s["unauthorized"])
            return
        user_states[user_id] = {'action': 'awaiting_edit', 'post_id': post_id}
        await query.edit_message_text(f"Editing post `{post['code']}`:\n" + s["edit_prompt"],
                                      parse_mode="Markdown", reply_markup=cancel_keyboard(lang))
    elif data.startswith("confirm_delete_"):
        post_id = int(data.split("_")[2])
        await delete_post(post_id, user_id)
        await query.edit_message_text(s["post_deleted"], reply_markup=main_menu_keyboard(lang))
    elif data == "cancel_action":
        if user_id in user_states:
            del user_states[user_id]
        await query.edit_message_text(s["cancel_text"], reply_markup=main_menu_keyboard(lang))

    else:
        await query.edit_message_text("Unknown action.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id)
    lang = await get_user_lang(user_id)
    s = STRINGS[lang]

    if state and state['action'] == 'awaiting_post':
        # Parse format: text | link | [color_emoji]
        parts = [p.strip() for p in text.split('|')]
        if len(parts) < 2 or len(parts) > 3:
            await update.message.reply_text(s["invalid_format"])
            return
        post_text = parts[0]
        link = parts[1]
        color_emoji = parts[2] if len(parts) == 3 else '🔵'
        if not link.startswith(('http://', 'https://')):
            await update.message.reply_text("❌ Invalid link. Must start with http:// or https://")
            return
        code = await create_post(user_id, post_text, link, color_emoji)
        del user_states[user_id]
        await update.message.reply_text(s["post_created"].format(code=code),
                                        reply_markup=main_menu_keyboard(lang))
    elif state and state['action'] == 'awaiting_edit':
        # Parse similar
        parts = [p.strip() for p in text.split('|')]
        if len(parts) < 2 or len(parts) > 3:
            await update.message.reply_text(s["invalid_format"])
            return
        post_text = parts[0]
        link = parts[1]
        color_emoji = parts[2] if len(parts) == 3 else '🔵'
        post_id = state['post_id']
        post = await get_post_by_id(post_id)
        if not post or post['user_id'] != user_id:
            await update.message.reply_text(s["unauthorized"])
            del user_states[user_id]
            return
        await update_post(post_id, user_id, post_text, link, color_emoji)
        del user_states[user_id]
        await update.message.reply_text(s["post_updated"], reply_markup=main_menu_keyboard(lang))
    else:
        # If not in any state, just show menu
        await update.message.reply_text(s["start"], reply_markup=main_menu_keyboard(lang))

async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.inline_query.query.strip()
    user_id = update.inline_query.from_user.id
    lang = await get_user_lang(user_id)
    results = []

    if not query_text:
        # Show user's own posts
        posts = await get_user_posts(user_id, limit=20)
        for p in posts:
            button_text = f"{p['color_emoji']} {p['text']}"
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=p['link'])]])
            # Use code as title
            result = InlineQueryResultArticle(
                id=str(p['id']),
                title=f"📌 {p['code']} : {p['text'][:30]}",
                input_message_content=InputTextMessageContent(message_text=f"🔗 {p['text']}"),
                reply_markup=markup,
                description=p['link']
            )
            results.append(result)
    else:
        # Search by code
        post = await get_post_by_code(query_text.upper())
        if post:
            button_text = f"{post['color_emoji']} {post['text']}"
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=post['link'])]])
            result = InlineQueryResultArticle(
                id=str(post['id']),
                title=f"📌 {post['code']} : {post['text'][:30]}",
                input_message_content=InputTextMessageContent(message_text=f"🔗 {post['text']}"),
                reply_markup=markup,
                description=post['link']
            )
            results.append(result)

    await update.inline_query.answer(results, cache_time=0)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} caused error {context.error}")

# ---------- Main ----------
async def main():
    await init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(InlineQueryHandler(inline_query_handler))
    app.add_error_handler(error_handler)

    # Commands for easier access
    app.add_handler(CommandHandler("myposts", lambda u, c: button_handler(u, c)))  # redirect

    # Start bot
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    random.seed()
    asyncio.run(main())
