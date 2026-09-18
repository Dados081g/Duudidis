"""
Скрипт запускается ОДИН РАЗ у вас локально (нужны интернет и токен бота).
Он скачивает картинки ваших premium-эмодзи через Bot API и собирает
готовый menu.html, который дальше нужно захостить на HTTPS
(GitHub Pages / Netlify / Vercel — любой бесплатный статик-хостинг)
и указать ссылку на него в bot.py в переменной WEBAPP_URL.

Запуск:
    pip install aiogram
    python build_menu.py
"""

import asyncio
import base64

from aiogram import Bot

BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"  # тот же токен, что и в bot.py

# Реальные ID premium-эмодзи, которые вы присылали
SECTION_EMOJI_IDS = {
    "EMOJI_BUY": "5258508428212445001",       # Купить товар
    "EMOJI_PROFILE": "5258513401784573443",   # Профиль
    "EMOJI_REVIEWS": "5257965174979042426",   # Отзывы
    "EMOJI_SUPPORT": "5260268501515377807",   # Поддержка
}

# Для этих ID не присылали — используем обычные emoji-картинки (Twemoji CDN)
FALLBACK_ICONS = {
    "EMOJI_KEYS": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f512.png",   # 🔒
    "EMOJI_LANG": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f319.png",   # 🌙
}


async def fetch_emoji_as_data_uri(bot: Bot, custom_emoji_id: str) -> str:
    """Скачивает статичную превью-картинку premium-эмодзи и возвращает как data URI."""
    stickers = await bot.get_custom_emoji_stickers(custom_emoji_ids=[custom_emoji_id])
    if not stickers:
        raise RuntimeError(f"Эмодзи с ID {custom_emoji_id} не найдено")

    sticker = stickers[0]
    # thumbnail — статичная превьюшка (jpeg/webp), подходит даже для анимированных эмодзи
    file_id = sticker.thumbnail.file_id if sticker.thumbnail else sticker.file_id
    file = await bot.get_file(file_id)
    file_bytes = await bot.download_file(file.file_path)
    data = file_bytes.read()

    mime = "image/webp" if file.file_path.endswith(".webp") else "image/jpeg"
    encoded = base64.b64encode(data).decode()
    return f"data:{mime};base64,{encoded}"


async def main():
    bot = Bot(token=BOT_TOKEN)

    replacements = {}
    for placeholder, emoji_id in SECTION_EMOJI_IDS.items():
        print(f"Скачиваю {placeholder} ({emoji_id})...")
        replacements[placeholder] = await fetch_emoji_as_data_uri(bot, emoji_id)

    replacements.update(FALLBACK_ICONS)

    with open("menu_template.html", "r", encoding="utf-8") as f:
        html = f.read()

    for placeholder, value in replacements.items():
        html = html.replace("{{" + placeholder + "}}", value)

    with open("menu.html", "w", encoding="utf-8") as f:
        f.write(html)

    await bot.session.close()
    print("\nГотово! Файл menu.html собран.")
    print("Дальше: захостите menu.html на HTTPS (GitHub Pages / Netlify / Vercel)")
    print("и вставьте ссылку в bot.py в переменную WEBAPP_URL.")


if __name__ == "__main__":
    asyncio.run(main())
