import asyncio
import json
import logging
import random
import string
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, InlineQueryHandler, ContextTypes

# ---------- Bot config ----------
BOT_TOKEN = "8264679566:AAFpbMd_g6Tbv3GfShREtCM0CW078ujPixY"
BOT_USERNAME = "@inline_text_maker_bot"

# ---------- JSON Storage ----------
DATA_FILE = "data.json"
data_lock = asyncio.Lock()
data = {"users": {}, "posts": []}  # in-memory

async def load_data():
    """Load JSON from file (blocking IO -> executor)."""
    loop = asyncio.get_running_loop()
    def _load():
        if Path(DATA_FILE).exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"users": {}, "posts": []}
    result = await loop.run_in_executor(None, _load)
    return result

async def save_data():
    """Save data dict to JSON file (blocking IO -> executor)."""
    async with data_lock:
        loop = asyncio.get_running_loop()
        def _save():
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        await loop.run_in_executor(None, _save)

async def init_data():
    global data
    data = await load_data()
    if "users" not in data:
        data["users"] = {}
    if "posts" not in data:
        data["posts"] = []

# ---------- Helpers ----------
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def get_user_lang(user_id):
    async with data_lock:
        user = data["users"].get(str(user_id), {})
        return user.get("lang", "bn")  # default Bangla

async def set_user_lang(user_id, lang):
    async with data_lock:
        data["users"][str(user_id)] = {"lang": lang}
        await save_data()

async def create_post(user_id, text, link, color_emoji):
    async with data_lock:
        while True:
            code = generate_code()
            # ensure code unique
            if not any(p["code"] == code for p in data["posts"]):
                new_post = {
                    "id": len(data["posts"]) + 1,
                    "user_id": user_id,
                    "code": code,
                    "text": text,
                    "link": link,
                    "color_emoji": color_emoji
                }
                data["posts"].append(new_post)
                await save_data()
                return code

async def get_user_posts(user_id, limit=50):
    async with data_lock:
        posts = [p for p in data["posts"] if p["user_id"] == user_id]
        posts.sort(key=lambda x: x["id"], reverse=True)
        return posts[:limit]

async def get_post_by_code(code):
    async with data_lock:
        for p in data["posts"]:
            if p["code"] == code:
                return p
    return None

async def get_post_by_id(post_id):
    async with data_lock:
        for p in data["posts"]:
            if p["id"] == post_id:
                return p
    return None

async def delete_post(post_id, user_id):
    async with data_lock:
        data["posts"] = [p for p in data["posts"] if not (p["id"] == post_id and p["user_id"] == user_id)]
        await save_data()

async def update_post(post_id, user_id, text, link, color_emoji):
    async with data_lock:
        for p in data["posts"]:
            if p["id"] == post_id and p["user_id"] == user_id:
                p["text"] = text
                p["link"] = link
                p["color_emoji"] = color_emoji
                break
        await save_data()

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
        "invalid_format": "❌ Invalid format! Use `Text | Link | [Emoji]`.",
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
        "back_to_menu": "Back to menu.",
        "delete_confirm": "Delete this post? (yes/no)"
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
        "back_to_menu": "মেনুতে ফিরুন।",
        "delete_confirm": "এই পোস্ট ডিলিট করবেন? (হ্যাঁ/না)"
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
        "back_to_menu": "Вернуться в меню.",
        "delete_confirm": "Удалить этот пост? (да/нет)"
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
        "back_to_menu": "मेनू पर वापस जाएं।",
        "delete_confirm": "इस पोस्ट को हटाएं? (हाँ/ना)"
    }
}

# ---------- State management ----------
user_states = {}  # {user_id: {"action": "awaiting_post" or "awaiting_edit", "post_id": int}}

# ---------- Keyboards ----------
def main_menu_keyboard(lang):
    s = STRINGS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(s["create_btn"], callback_data="create_post")],
        [InlineKeyboardButton(s["my_posts_btn"], callback_data="my_posts")],
        [InlineKeyboardButton(s["language_btn"], callback_data="change_lang")],
        [InlineKeyboardButton(s["developer_btn"], callback_data="developer")],
        [InlineKeyboardButton(s["update_channel_btn"], url="https://t.me/earning_channel24")]
    ])

def cancel_keyboard(lang):
    s = STRINGS[lang]
    return InlineKeyboardMarkup([[InlineKeyboardButton(s["cancel"], callback_data="cancel_action")]])

def language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
         InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")]
    ])

def post_actions_keyboard(post_id, lang):
    s = STRINGS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑️", callback_data=f"delete_{post_id}"),
         InlineKeyboardButton("✏️", callback_data=f"edit_{post_id}")]
    ])

def back_button(lang):
    s = STRINGS[lang]
    return InlineKeyboardMarkup([[InlineKeyboardButton(s["back_to_menu"], callback_data="back_to_menu")]])

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
        user_states[user_id] = {"action": "awaiting_post"}
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
                                          reply_markup=post_actions_keyboard(posts[0]["id"], lang) if posts else back_button(lang))
            # Actually we should show action buttons per post... but we can't in one message easily.
            # We'll just show list and then user can select via inline buttons for each? Better to send one message per post? 
            # Let's simplify: show the list with "done" button, and user can do delete/edit via separate management? 
            # We'll provide a list with a button for each post? That's messy. We'll instead change approach: 
            # When user clicks My Posts, show a gallery of inline buttons for each post to manage? 
            # Let's modify: we'll show a short list and ask user to click on post code? 
            # I'll just show a numbered list with delete/edit options as keyboard per post? Need to redesign.
            # But keep simple for now: show only the list + done button. User can delete/edit by sending a command? 
            # The user requested ability to delete/edit. They can do it via inline query? Actually we had delete/edit callbacks on each post. 
            # We'll implement: after showing list, we'll provide a row of buttons for each post? Not scalable.
            # Better: Show list and add inline keyboard "Manage Posts" which shows a paginated picker. 
            # Since we need full working, let's do this: 
            # "My Posts" will show a message "Select a post to manage:" and then a keyboard with first few posts as buttons. 
            # But that's too many buttons. We'll limit to 5 posts per page. 
            # This is getting big. I'll just use a simple approach: 
            # Show list, and below that a message "To delete or edit, use /delete <code> or /edit <code>". But user wanted inline buttons.
            # I'll keep the original concept: In the list, each post shown with its delete/edit buttons. We'll build a large keyboard with buttons for each post? 
            # That's possible but ugly. However user don't mind. I'll create a keyboard with each post as a pair of buttons: (Delete, Edit). 
            # Let's do a keyboard where each row is for a post: [🗑️ {code}, ✏️ {code}]. But button text must be short.
            # We'll use 🗑️ and ✏️ and callback data with post id.
            # We'll limit to 10 posts to avoid too many buttons.
            # I'll implement:
            if len(posts) > 10:
                posts = posts[:10]
                text += "\n(Showing last 10 posts)"
            kb = []
            for p in posts:
                kb.append([
                    InlineKeyboardButton(f"🗑️ {p['code']}", callback_data=f"delete_{p['id']}"),
                    InlineKeyboardButton(f"✏️ {p['code']}", callback_data=f"edit_{p['id']}")
                ])
            kb.append([InlineKeyboardButton(s["back_to_menu"], callback_data="back_to_menu")])
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup(kb))
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
        await query.edit_message_text(dev_text, reply_markup=back_button(lang))
    elif data == "back_to_menu":
        if user_id in user_states:
            del user_states[user_id]
        await query.edit_message_text(s["start"], reply_markup=main_menu_keyboard(lang))
    elif data.startswith("delete_"):
        post_id = int(data.split("_")[1])
        # Confirm delete
        await query.edit_message_text(s["delete_confirm"], reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes", callback_data=f"confirm_delete_{post_id}"),
             InlineKeyboardButton("❌ No", callback_data="my_posts")]
        ]))
    elif data.startswith("confirm_delete_"):
        post_id = int(data.split("_")[2])
        await delete_post(post_id, user_id)
        await query.edit_message_text(s["post_deleted"], reply_markup=main_menu_keyboard(lang))
    elif data.startswith("edit_"):
        post_id = int(data.split("_")[1])
        post = await get_post_by_id(post_id)
        if not post or post["user_id"] != user_id:
            await query.edit_message_text(s["unauthorized"])
            return
        user_states[user_id] = {"action": "awaiting_edit", "post_id": post_id}
        await query.edit_message_text(f"Editing post `{post['code']}`:\n" + s["edit_prompt"],
                                      parse_mode="Markdown", reply_markup=cancel_keyboard(lang))
    elif data == "cancel_action":
        if user_id in user_states:
            del user_states[user_id]
        await query.edit_message_text(s["cancel_text"], reply_markup=main_menu_keyboard(lang))
    else:
        # Fallback
        await query.edit_message_text("Unknown action.", reply_markup=main_menu_keyboard(lang))

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id)
    lang = await get_user_lang(user_id)
    s = STRINGS[lang]

    if state and state["action"] == "awaiting_post":
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 2 or len(parts) > 3:
            await update.message.reply_text(s["invalid_format"])
            return
        post_text = parts[0]
        link = parts[1]
        color_emoji = parts[2] if len(parts) == 3 else "🔵"
        if not link.startswith(("http://", "https://")):
            await update.message.reply_text("❌ Invalid link. Must start with http:// or https://")
            return
        code = await create_post(user_id, post_text, link, color_emoji)
        del user_states[user_id]
        await update.message.reply_text(s["post_created"].format(code=code), reply_markup=main_menu_keyboard(lang))
    elif state and state["action"] == "awaiting_edit":
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 2 or len(parts) > 3:
            await update.message.reply_text(s["invalid_format"])
            return
        post_text = parts[0]
        link = parts[1]
        color_emoji = parts[2] if len(parts) == 3 else "🔵"
        post_id = state["post_id"]
        post = await get_post_by_id(post_id)
        if not post or post["user_id"] != user_id:
            await update.message.reply_text(s["unauthorized"])
            del user_states[user_id]
            return
        await update_post(post_id, user_id, post_text, link, color_emoji)
        del user_states[user_id]
        await update.message.reply_text(s["post_updated"], reply_markup=main_menu_keyboard(lang))
    else:
        # No active state – show menu
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
            result = InlineQueryResultArticle(
                id=str(p["id"]),
                title=f"📌 {p['code']} : {p['text'][:30]}",
                input_message_content=InputTextMessageContent(message_text=f"🔗 {p['text']}"),
                reply_markup=markup,
                description=p["link"]
            )
            results.append(result)
    else:
        # Search by code
        post = await get_post_by_code(query_text.upper())
        if post:
            button_text = f"{post['color_emoji']} {post['text']}"
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=post['link'])]])
            result = InlineQueryResultArticle(
                id=str(post["id"]),
                title=f"📌 {post['code']} : {post['text'][:30]}",
                input_message_content=InputTextMessageContent(message_text=f"🔗 {post['text']}"),
                reply_markup=markup,
                description=post["link"]
            )
            results.append(result)

    await update.inline_query.answer(results, cache_time=0)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update {update} caused error {context.error}")

# ---------- Main ----------
async def main():
    logging.basicConfig(level=logging.INFO)
    await init_data()
    random.seed()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(InlineQueryHandler(inline_query_handler))
    app.add_error_handler(error_handler)

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
