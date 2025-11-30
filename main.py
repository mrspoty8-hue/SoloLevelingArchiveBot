import logging
import os
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import (
    CHANNEL_ID, WELCOME_MESSAGE, SEASON_1_INFO, SEASON_2_INFO,
    DELETE_NOTIFICATION, AUTO_DELETE_SECONDS
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def schedule_message_deletion(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Deleted message {message_id} from chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to delete message {message_id}: {e}")


def get_season_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Season 1", callback_data="season_1"),
            InlineKeyboardButton("Season 2", callback_data="season_2"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_episodes_keyboard(season: int):
    season_info = SEASON_1_INFO if season == 1 else SEASON_2_INFO
    episodes = list(season_info["episodes"].keys())
    
    keyboard = []
    row = []
    for i, ep in enumerate(episodes):
        row.append(InlineKeyboardButton(f"Ep {ep}", callback_data=f"episode_{season}_{ep}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_seasons")])
    
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = get_season_keyboard()
    await update.message.reply_text(
        WELCOME_MESSAGE + "\n\nWhat do you want to watch?",
        reply_markup=keyboard
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "season_1":
        await handle_season_selection(query, context, 1)
    elif data == "season_2":
        await handle_season_selection(query, context, 2)
    elif data == "back_to_seasons":
        keyboard = get_season_keyboard()
        await query.edit_message_text(
            WELCOME_MESSAGE + "\n\nWhat do you want to watch?",
            reply_markup=keyboard
        )
    elif data.startswith("episode_"):
        parts = data.split("_")
        season = int(parts[1])
        episode = int(parts[2])
        await handle_episode_selection(query, context, season, episode)
    elif data.startswith("back_to_episodes_"):
        season = int(data.split("_")[-1])
        keyboard = get_episodes_keyboard(season)
        season_name = "Season 1" if season == 1 else "Season 2"
        await query.edit_message_text(
            f"You selected {season_name}!\n\nChoose an episode:",
            reply_markup=keyboard
        )


async def handle_season_selection(query, context: ContextTypes.DEFAULT_TYPE, season: int):
    season_info = SEASON_1_INFO if season == 1 else SEASON_2_INFO
    chat_id = query.message.chat_id
    
    try:
        await query.message.delete()
    except Exception as e:
        logger.error(f"Failed to delete original message: {e}")
    
    messages_to_delete = []
    
    if season_info["message_id"]:
        try:
            forwarded = await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=CHANNEL_ID,
                message_id=season_info["message_id"]
            )
            messages_to_delete.append(forwarded.message_id)
        except Exception as e:
            logger.error(f"Failed to forward season message: {e}")
    
    if messages_to_delete:
        notification = await context.bot.send_message(
            chat_id=chat_id,
            text=DELETE_NOTIFICATION
        )
        messages_to_delete.append(notification.message_id)
        
        for msg_id in messages_to_delete:
            asyncio.create_task(schedule_message_deletion(context, chat_id, msg_id))
    
    keyboard = get_episodes_keyboard(season)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"You selected {season_info['name']}!\n\nChoose an episode:",
        reply_markup=keyboard
    )


async def handle_episode_selection(query, context: ContextTypes.DEFAULT_TYPE, season: int, episode: int):
    season_info = SEASON_1_INFO if season == 1 else SEASON_2_INFO
    episode_info = season_info["episodes"].get(episode, {})
    chat_id = query.message.chat_id
    
    photo_id = episode_info.get("photo_message_id")
    details_id = episode_info.get("details_message_id")
    
    messages_to_delete = []
    
    if photo_id:
        try:
            forwarded = await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=CHANNEL_ID,
                message_id=photo_id
            )
            messages_to_delete.append(forwarded.message_id)
        except Exception as e:
            logger.error(f"Failed to forward photo message: {e}")
    
    if details_id:
        try:
            forwarded = await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=CHANNEL_ID,
                message_id=details_id
            )
            messages_to_delete.append(forwarded.message_id)
        except Exception as e:
            logger.error(f"Failed to forward details message: {e}")
    
    if messages_to_delete:
        notification = await context.bot.send_message(
            chat_id=chat_id,
            text=DELETE_NOTIFICATION
        )
        messages_to_delete.append(notification.message_id)
        
        for msg_id in messages_to_delete:
            asyncio.create_task(schedule_message_deletion(context, chat_id, msg_id))
    
    keyboard = [[InlineKeyboardButton("Back to Episodes", callback_data=f"back_to_episodes_{season}")]]
    
    if len(messages_to_delete) == 0:
        await query.edit_message_text(
            f"Season {season} - Episode {episode}\n\n(No content configured yet)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text(
            f"Season {season} - Episode {episode}\n\nHere's the episode info! 👆",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start browsing episodes\n"
        "/help - Show this help message"
    )


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
