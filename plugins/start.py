from pyrofork import Client, filters
from pyrofork.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import Users
from config import START_MESSAGE, START_IMAGE_URL, SUPPORT_CHAT_URL, UPDATE_CHANNEL_URL

# Start command handler
@Client.on_message(filters.command("start") & filters.incoming)
async def start_command(client: Client, message: Message):
    # Add user to database
    if message.from_user:
        await Users.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
    
    # Create inline keyboard with buttons
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help_main"),
            InlineKeyboardButton("👤 About", callback_data="about")
        ],
        [
            InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT_URL),
            InlineKeyboardButton("📢 Updates Channel", url=UPDATE_CHANNEL_URL)
        ]
    ])
    
    # Send welcome message with image
    try:
        await message.reply_photo(
            photo=START_IMAGE_URL,
            caption=START_MESSAGE,
            reply_markup=keyboard
        )
    except Exception as e:
        # Fallback to text message if image can't be sent
        await message.reply_text(
            text=f"{START_MESSAGE}\n\nNote: Could not send image due to an error.",
            reply_markup=keyboard
        )


# About callback handler
@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client, callback_query):
    about_text = (
        "**Jotaro Kujo Bot**\n\n"
        "A powerful group management bot with the spirit of Jotaro Kujo.\n\n"
        "**Stand Power**: Star Platinum\n"
        "**Special Ability**: Group moderation with precision and speed\n\n"
        "Use /help to see what I can do."
    )
    
    back_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="start_back")]
    ])
    
    await callback_query.edit_message_caption(
        caption=about_text,
        reply_markup=back_button
    )


# Back to start callback handler
@Client.on_callback_query(filters.regex("^start_back$"))
async def start_back_callback(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help_main"),
            InlineKeyboardButton("👤 About", callback_data="about")
        ],
        [
            InlineKeyboardButton("💬 Support Chat", url=SUPPORT_CHAT_URL),
            InlineKeyboardButton("📢 Updates Channel", url=UPDATE_CHANNEL_URL)
        ]
    ])
    
    await callback_query.edit_message_caption(
        caption=START_MESSAGE,
        reply_markup=keyboard
    )
