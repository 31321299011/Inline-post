import telebot
from telebot import types
import sqlite3
import string
import random
import re

TOKEN = "8264679566:AAFpbMd_g6Tbv3GfShREtCM0CW078ujPixY"
BOT_USERNAME = "@inline_text_maker_bot"

bot = telebot.TeleBot(TOKEN)

# ---------- DATABASE ----------
conn = sqlite3.connect('posts.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'en'
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    code TEXT UNIQUE,
    text TEXT,
    url TEXT,
    color TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
)
''')
conn.commit()

# ---------- LANGUAGE DICTIONARIES ----------
LANG = {
    'en': {
        'start': "🌟 Welcome to *Inline Text Maker* 💠\n\nCreate beautiful inline buttons with coloured boxes.\nUse the menu below or type /help for more.",
        'help': "📘 How to use:\n1. Click `Create Inline Link`\n2. Send button text\n3. Send URL\n4. Choose a box colour\n\nAfter saving, you'll get a code. Use it in any chat like this:\n`@inline_text_maker_bot CODE`\nThe bot will show your button directly in the chat!",
        'choose_lang': "🌐 Please choose your language:",
        'lang_set': "✅ Language set to English.",
        'create_prompt_text': "📝 Send the button text:",
        'create_prompt_url': "🔗 Now send the URL (must start with http:// or https://):",
        'invalid_url': "❌ Invalid URL. Please send a valid link starting with http:// or https://.",
        'choose_color': "🎨 Choose a box colour for your button:",
        'color_red': "🔴 Red",
        'color_green': "🟢 Green",
        'color_blue': "🔵 Blue",
        'color_yellow': "🟡 Yellow",
        'color_purple': "🟣 Purple",
        'color_orange': "🟠 Orange",
        'post_saved': "✅ Post saved! Code: `{code}`\n\nYou can use it in inline mode:\n`{bot_username} {code}`\n\nPreview:\n{preview}",
        'post_deleted': "🗑 Post deleted.",
        'no_posts': "📭 You have no saved posts.",
        'my_posts': "📋 Your saved posts:",
        'edit_choose': "✏️ Which post do you want to edit?",
        'edit_field': "✏️ Choose what to edit:",
        'edit_text_prompt': "📝 Send new button text:",
        'edit_url_prompt': "🔗 Send new URL:",
        'edit_color_prompt': "🎨 Choose new colour:",
        'post_updated': "✅ Post updated.",
    },
    'bn': {
        'start': "🌟 স্বাগতম *ইনলাইন টেক্সট মেকার* 💠\n\nসুন্দর রঙিন বক্স বাটন তৈরি করুন।\nনিচের মেনু ব্যবহার করুন বা /help দেখুন।",
        'help': "📘 কিভাবে ব্যবহার করবেন:\n1. `Create Inline Link` বাটনে ক্লিক করুন\n2. বাটনের টেক্সট দিন\n3. URL দিন\n4. বক্সের রঙ নির্বাচন করুন\n\nসংরক্ষণের পর একটি কোড পাবেন। যেকোনো চ্যাটে এই ফরম্যাটে ব্যবহার করুন:\n`@inline_text_maker_bot কোড`\nবট সরাসরি বাটন দেখাবে!",
        'choose_lang': "🌐 অনুগ্রহ করে ভাষা নির্বাচন করুন:",
        'lang_set': "✅ ভাষা বাংলায় সেট করা হয়েছে।",
        'create_prompt_text': "📝 বাটনের টেক্সট পাঠান:",
        'create_prompt_url': "🔗 এখন URL পাঠান (http:// বা https:// সহ):",
        'invalid_url': "❌ অবৈধ URL। অনুগ্রহ করে সঠিক লিংক দিন।",
        'choose_color': "🎨 আপনার বাটনের জন্য একটি বক্স রঙ নির্বাচন করুন:",
        'color_red': "🔴 লাল",
        'color_green': "🟢 সবুজ",
        'color_blue': "🔵 নীল",
        'color_yellow': "🟡 হলুদ",
        'color_purple': "🟣 বেগুনি",
        'color_orange': "🟠 কমলা",
        'post_saved': "✅ পোস্ট সংরক্ষিত! কোড: `{code}`\n\nইনলাইন মোডে ব্যবহার করুন:\n`{bot_username} {code}`\n\nপ্রিভিউ:\n{preview}",
        'post_deleted': "🗑 পোস্ট ডিলিট হয়েছে।",
        'no_posts': "📭 আপনার কোনো পোস্ট নেই।",
        'my_posts': "📋 আপনার সংরক্ষিত পোস্ট:",
        'edit_choose': "✏️ কোন পোস্ট সম্পাদনা করতে চান?",
        'edit_field': "✏️ কি পরিবর্তন করবেন?",
        'edit_text_prompt': "📝 নতুন বাটনের টেক্সট দিন:",
        'edit_url_prompt': "🔗 নতুন URL দিন:",
        'edit_color_prompt': "🎨 নতুন রঙ নির্বাচন করুন:",
        'post_updated': "✅ পোস্ট আপডেট হয়েছে।",
    },
    'ru': {
        'start': "🌟 Добро пожаловать в *Inline Text Maker* 💠\n\nСоздавайте красивые цветные кнопки.\nИспользуйте меню или /help.",
        'help': "📘 Как использовать:\n1. Нажмите `Create Inline Link`\n2. Отправьте текст кнопки\n3. Отправьте URL\n4. Выберите цвет рамки\n\nПосле сохранения вы получите код. Используйте его в любом чате:\n`@inline_text_maker_bot КОД`\nБот покажет вашу кнопку прямо в чате!",
        'choose_lang': "🌐 Выберите язык:",
        'lang_set': "✅ Язык установлен на русский.",
        'create_prompt_text': "📝 Отправьте текст кнопки:",
        'create_prompt_url': "🔗 Теперь отправьте URL (начинается с http:// или https://):",
        'invalid_url': "❌ Неверная ссылка. Отправьте корректную.",
        'choose_color': "🎨 Выберите цвет кнопки:",
        'color_red': "🔴 Красный",
        'color_green': "🟢 Зелёный",
        'color_blue': "🔵 Синий",
        'color_yellow': "🟡 Жёлтый",
        'color_purple': "🟣 Фиолетовый",
        'color_orange': "🟠 Оранжевый",
        'post_saved': "✅ Пост сохранён! Код: `{code}`\n\nИспользуйте в инлайн-режиме:\n`{bot_username} {code}`\n\nПредпросмотр:\n{preview}",
        'post_deleted': "🗑 Пост удалён.",
        'no_posts': "📭 У вас нет сохранённых постов.",
        'my_posts': "📋 Ваши сохранённые посты:",
        'edit_choose': "✏️ Какой пост редактировать?",
        'edit_field': "✏️ Что изменить?",
        'edit_text_prompt': "📝 Новый текст кнопки:",
        'edit_url_prompt': "🔗 Новая ссылка:",
        'edit_color_prompt': "🎨 Новый цвет:",
        'post_updated': "✅ Пост обновлён.",
    },
    'hi': {
        'start': "🌟 *इनलाइन टेक्स्ट मेकर* 💠 में आपका स्वागत है\n\nखूबसूरत रंगीन बॉक्स बटन बनाएं।\nनीचे मेनू का उपयोग करें या /help देखें।",
        'help': "📘 उपयोग कैसे करें:\n1. `Create Inline Link` पर क्लिक करें\n2. बटन का टेक्स्ट भेजें\n3. URL भेजें\n4. बॉक्स का रंग चुनें\n\nसेव करने के बाद आपको एक कोड मिलेगा। किसी भी चैट में:\n`@inline_text_maker_bot कोड`\nबॉट आपका बटन सीधे चैट में दिखाएगा!",
        'choose_lang': "🌐 कृपया भाषा चुनें:",
        'lang_set': "✅ भाषा हिंदी में सेट की गई।",
        'create_prompt_text': "📝 बटन टेक्स्ट भेजें:",
        'create_prompt_url': "🔗 अब URL भेजें (http:// या https:// से शुरू):",
        'invalid_url': "❌ अमान्य लिंक। कृपया सही लिंक दें।",
        'choose_color': "🎨 अपने बटन का रंग चुनें:",
        'color_red': "🔴 लाल",
        'color_green': "🟢 हरा",
        'color_blue': "🔵 नीला",
        'color_yellow': "🟡 पीला",
        'color_purple': "🟣 बैंगनी",
        'color_orange': "🟠 नारंगी",
        'post_saved': "✅ पोस्ट सहेजा गया! कोड: `{code}`\n\nइनलाइन मोड में उपयोग:\n`{bot_username} {code}`\n\nप्रीव्यू:\n{preview}",
        'post_deleted': "🗑 पोस्ट हटा दी गई।",
        'no_posts': "📭 आपके पास कोई पोस्ट नहीं है।",
        'my_posts': "📋 आपकी सहेजी गई पोस्ट:",
        'edit_choose': "✏️ कौन सी पोस्ट एडिट करें?",
        'edit_field': "✏️ क्या बदलें?",
        'edit_text_prompt': "📝 नया बटन टेक्स्ट दें:",
        'edit_url_prompt': "🔗 नया URL दें:",
        'edit_color_prompt': "🎨 नया रंग चुनें:",
        'post_updated': "✅ पोस्ट अपडेट हुई।",
    }
}

# ---------- HELPERS ----------
def get_lang(user_id):
    cursor.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 'en'

def set_lang(user_id, lang):
    cursor.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, lang))
    conn.commit()

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def color_emoji(color):
    return {'red': '🔴','green': '🟢','blue': '🔵','yellow': '🟡','purple': '🟣','orange': '🟠'}.get(color, '⚪')

def url_valid(url):
    return re.match(r'https?://', url) is not None

# ---------- KEYBOARDS ----------
def lang_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
               types.InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn"))
    markup.add(types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
               types.InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi"))
    return markup

def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💠 Create Inline Link", "📋 My Posts")
    markup.add("🌐 Language", "ℹ️ Help")
    return markup

def color_keyboard():
    markup = types.InlineKeyboardMarkup()
    colors = [('red', '🔴 Red'), ('green', '🟢 Green'), ('blue', '🔵 Blue'),
              ('yellow', '🟡 Yellow'), ('purple', '🟣 Purple'), ('orange', '🟠 Orange')]
    buttons = [types.InlineKeyboardButton(text=name, callback_data=f"color_{color}") for color, name in colors]
    markup.add(*buttons)
    return markup

def edit_field_keyboard(post_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 Text", callback_data=f"edittext_{post_id}"),
               types.InlineKeyboardButton("🔗 URL", callback_data=f"editurl_{post_id}"))
    markup.add(types.InlineKeyboardButton("🎨 Colour", callback_data=f"editcolor_{post_id}"),
               types.InlineKeyboardButton("❌ Cancel", callback_data="edit_cancel"))
    return markup

# ---------- COMMANDS ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    # if language not set, ask
    cursor.execute("SELECT language FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        bot.send_message(user_id, LANG['en']['choose_lang'], reply_markup=lang_keyboard())
    else:
        bot.send_message(user_id, LANG[lang]['start'], parse_mode='Markdown', reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['help'])
def help_cmd(message):
    lang = get_lang(message.from_user.id)
    bot.send_message(message.chat.id, LANG[lang]['help'], parse_mode='Markdown', reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['language'])
def set_language_cmd(message):
    bot.send_message(message.chat.id, "🌐 Choose language:", reply_markup=lang_keyboard())

@bot.message_handler(commands=['myposts'])
def list_posts_cmd(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    cursor.execute("SELECT id, code, text, url, color FROM posts WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        bot.send_message(user_id, LANG[lang]['no_posts'])
        return
    text = LANG[lang]['my_posts'] + "\n\n"
    markup = types.InlineKeyboardMarkup()
    for post_id, code, ptext, url, color in rows:
        emoji = color_emoji(color)
        btn_text = f"{emoji} {ptext}"
        text += f"• `{code}` → [{btn_text}]({url})\n"
        markup.add(types.InlineKeyboardButton(f"✏️ Edit {ptext[:15]}", callback_data=f"editmenu_{post_id}"),
                   types.InlineKeyboardButton(f"🗑 Delete {code}", callback_data=f"delete_{post_id}"))
    bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup, disable_web_page_preview=True)

# ---------- FLOW CONTROL (Create) ----------
user_step = {}  # user_id: step and data

@bot.message_handler(func=lambda m: m.text == "💠 Create Inline Link")
def create_start(message):
    lang = get_lang(message.from_user.id)
    user_step[message.from_user.id] = {'step': 'text'}
    bot.send_message(message.chat.id, LANG[lang]['create_prompt_text'], reply_markup=types.ForceReply(selective=False))

@bot.message_handler(func=lambda m: user_step.get(m.from_user.id, {}).get('step') == 'text')
def receive_text(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    user_step[user_id]['text'] = message.text
    user_step[user_id]['step'] = 'url'
    bot.send_message(user_id, LANG[lang]['create_prompt_url'], reply_markup=types.ForceReply(selective=False))

@bot.message_handler(func=lambda m: user_step.get(m.from_user.id, {}).get('step') == 'url')
def receive_url(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    url = message.text.strip()
    if not url_valid(url):
        bot.send_message(user_id, LANG[lang]['invalid_url'])
        return
    user_step[user_id]['url'] = url
    user_step[user_id]['step'] = 'color'
    bot.send_message(user_id, LANG[lang]['choose_color'], reply_markup=color_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('color_') and user_step.get(call.from_user.id, {}).get('step') == 'color')
def receive_color(call):
    user_id = call.from_user.id
    lang = get_lang(user_id)
    color = call.data.split('_')[1]
    text = user_step[user_id]['text']
    url = user_step[user_id]['url']
    code = generate_code()
    # Save to DB
    try:
        cursor.execute("INSERT INTO posts (user_id, code, text, url, color) VALUES (?, ?, ?, ?, ?)",
                       (user_id, code, text, url, color))
        conn.commit()
    except sqlite3.IntegrityError:
        # regenerate code if collision
        code = generate_code()
        cursor.execute("INSERT INTO posts (user_id, code, text, url, color) VALUES (?, ?, ?, ?, ?)",
                       (user_id, code, text, url, color))
        conn.commit()
    post_id = cursor.lastrowid
    emoji = color_emoji(color)
    preview = f"[{emoji} {text}]({url})"
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, LANG[lang]['post_saved'].format(
        code=code, bot_username=BOT_USERNAME, preview=preview), parse_mode='Markdown', reply_markup=main_menu_keyboard())
    user_step.pop(user_id, None)

# ---------- EDIT / DELETE ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_post(call):
    user_id = call.from_user.id
    lang = get_lang(user_id)
    post_id = int(call.data.split('_')[1])
    cursor.execute("DELETE FROM posts WHERE id=? AND user_id=?", (post_id, user_id))
    conn.commit()
    bot.answer_callback_query(call.id, LANG[lang]['post_deleted'])
    bot.edit_message_text(LANG[lang]['post_deleted'], call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('editmenu_'))
def edit_menu(call):
    post_id = int(call.data.split('_')[1])
    lang = get_lang(call.from_user.id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, LANG[lang]['edit_field'], reply_markup=edit_field_keyboard(post_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith('edittext_'))
def edit_text_start(call):
    user_id = call.from_user.id
    post_id = int(call.data.split('_')[1])
    lang = get_lang(user_id)
    user_step[user_id] = {'step': 'edit_text', 'post_id': post_id}
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, LANG[lang]['edit_text_prompt'], reply_markup=types.ForceReply(selective=False))

@bot.callback_query_handler(func=lambda call: call.data.startswith('editurl_'))
def edit_url_start(call):
    user_id = call.from_user.id
    post_id = int(call.data.split('_')[1])
    lang = get_lang(user_id)
    user_step[user_id] = {'step': 'edit_url', 'post_id': post_id}
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, LANG[lang]['edit_url_prompt'], reply_markup=types.ForceReply(selective=False))

@bot.callback_query_handler(func=lambda call: call.data.startswith('editcolor_'))
def edit_color_start(call):
    user_id = call.from_user.id
    post_id = int(call.data.split('_')[1])
    lang = get_lang(user_id)
    user_step[user_id] = {'step': 'edit_color', 'post_id': post_id}
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, LANG[lang]['edit_color_prompt'], reply_markup=color_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == 'edit_cancel')
def edit_cancel(call):
    bot.answer_callback_query(call.id, "Cancelled.")
    bot.edit_message_text("Edit cancelled.", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: user_step.get(m.from_user.id, {}).get('step') in ('edit_text', 'edit_url'))
def receive_edit_field(message):
    user_id = message.from_user.id
    step = user_step[user_id]['step']
    post_id = user_step[user_id]['post_id']
    lang = get_lang(user_id)
    if step == 'edit_text':
        new_val = message.text
        cursor.execute("UPDATE posts SET text=? WHERE id=? AND user_id=?", (new_val, post_id, user_id))
    elif step == 'edit_url':
        if not url_valid(message.text.strip()):
            bot.send_message(user_id, LANG[lang]['invalid_url'])
            return
        new_val = message.text.strip()
        cursor.execute("UPDATE posts SET url=? WHERE id=? AND user_id=?", (new_val, post_id, user_id))
    conn.commit()
    bot.send_message(user_id, LANG[lang]['post_updated'])
    user_step.pop(user_id, None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('color_') and user_step.get(call.from_user.id, {}).get('step') == 'edit_color')
def edit_color_final(call):
    user_id = call.from_user.id
    post_id = user_step[user_id]['post_id']
    color = call.data.split('_')[1]
    cursor.execute("UPDATE posts SET color=? WHERE id=? AND user_id=?", (color, post_id, user_id))
    conn.commit()
    lang = get_lang(user_id)
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, LANG[lang]['post_updated'])
    user_step.pop(user_id, None)

# ---------- INLINE MODE ----------
@bot.inline_handler(lambda query: True)
def inline_query(inline_query):
    user_id = inline_query.from_user.id
    lang = get_lang(user_id)
    query = inline_query.query.strip()
    cursor.execute("SELECT id, code, text, url, color FROM posts WHERE user_id=?", (user_id,))
    if query:
        # search by code exactly
        cursor.execute("SELECT id, code, text, url, color FROM posts WHERE user_id=? AND code=?", (user_id, query))
        rows = cursor.fetchall()
    else:
        rows = cursor.fetchall()
    results = []
    for post_id, code, ptext, url, color in rows:
        emoji = color_emoji(color)
        # compose button
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=f"{emoji} {ptext}", url=url))
        # input message content
        msg_text = f"🌟 {ptext}" if lang == 'en' else f"🌟 {ptext}"
        input_content = types.InputTextMessageContent(msg_text, parse_mode='HTML')
        results.append(types.InlineQueryResultArticle(
            id=str(post_id),
            title=f"{ptext[:30]}",
            description=f"Go to {url[:40]}",
            input_message_content=input_content,
            reply_markup=markup,
            thumb_url="https://via.placeholder.com/50"  # optional tiny placeholder
        ))
    bot.answer_inline_query(inline_query.id, results, cache_time=1)

# ---------- LANGUAGE CALLBACK ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def lang_callback(call):
    lang = call.data.split('_')[1]
    user_id = call.from_user.id
    set_lang(user_id, lang)
    bot.answer_callback_query(call.id, LANG[lang]['lang_set'])
    bot.edit_message_text(LANG[lang]['lang_set'], call.message.chat.id, call.message.message_id)
    bot.send_message(user_id, LANG[lang]['start'], parse_mode='Markdown', reply_markup=main_menu_keyboard())

# ---------- EXTRA BUTTONS (Developer & Update) ----------
@bot.message_handler(func=lambda m: m.text == "ℹ️ Help")
def help_btn(m):
    help_cmd(m)

@bot.message_handler(func=lambda m: m.text == "🌐 Language")
def lang_btn(m):
    set_language_cmd(m)

@bot.message_handler(func=lambda m: m.text == "📋 My Posts")
def myposts_btn(m):
    list_posts_cmd(m)

# Start button for main menu after lang set
@bot.message_handler(commands=['menu'])
def menu_cmd(m):
    lang = get_lang(m.from_user.id)
    bot.send_message(m.chat.id, LANG[lang]['start'], reply_markup=main_menu_keyboard())

# Developer & Channel buttons (inline in start message)
# We'll add them to the start message directly. Already in main menu? We'll add a static inline keyboard.
# Actually, we'll modify main_menu to include ReplyKeyboard with extra buttons.
# Let's add "👨‍💻 Developer" and "🔔 Channel" as ReplyKeyboard buttons.
def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💠 Create Inline Link", "📋 My Posts")
    markup.add("🌐 Language", "ℹ️ Help")
    markup.add("👨‍💻 Developer", "🔔 Update Channel")
    return markup

@bot.message_handler(func=lambda m: m.text == "👨‍💻 Developer")
def dev_btn(m):
    bot.send_message(m.chat.id, "Developers:\n@Bot_developer_io & @jhgmaing", reply_markup=main_menu_keyboard())

@bot.message_handler(func=lambda m: m.text == "🔔 Update Channel")
def channel_btn(m):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/earning_channel24"))
    bot.send_message(m.chat.id, "Stay updated with our channel 👇", reply_markup=markup)

# ---------- POLLING ----------
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
