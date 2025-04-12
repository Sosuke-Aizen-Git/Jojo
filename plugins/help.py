from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import HELP_MESSAGE, HELP_GENERAL, HELP_ADMIN, HELP_UTILITY

# Help command handler
@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    # If no arguments, show main help message with buttons
    if len(message.command) == 1:
        # Create inline keyboard with categories
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌟 General", callback_data="help_general"),
                InlineKeyboardButton("⭐ Admin", callback_data="help_admin")
            ],
            [
                InlineKeyboardButton("💫 Utility", callback_data="help_utility")
            ]
        ])
        
        await message.reply_text(HELP_MESSAGE, reply_markup=keyboard)
        return
    
    # If category is specified, show category-specific help
    category = message.command[1].lower()
    
    if category == "general":
        await message.reply_text(HELP_GENERAL)
    elif category == "admin":
        await message.reply_text(HELP_ADMIN)
    elif category == "utility":
        await message.reply_text(HELP_UTILITY)
    else:
        await message.reply_text("Unknown help category. Available categories: general, admin, utility")

  # Help callback handler for buttons
@Client.on_callback_query(filters.regex('^help_'))
async def help_callback(client, callback_query):
    # Extract the category from callback data
    category = callback_query.data.split('_')[1]
    
    # Send appropriate help text based on category
    if category == "general":
        await callback_query.message.edit_text(
            HELP_GENERAL,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="help_back")]
            ])
        )
    elif category == "admin":
        await callback_query.message.edit_text(
            HELP_ADMIN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="help_back")]
            ])
        )
    elif category == "utility":
        await callback_query.message.edit_text(
            HELP_UTILITY,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="help_back")]
            ])
        )
    elif category == "back":
        # Return to main help menu
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌟 General", callback_data="help_general"),
                InlineKeyboardButton("⭐ Admin", callback_data="help_admin")
            ],
            [
                InlineKeyboardButton("💫 Utility", callback_data="help_utility")
            ]
        ])
        
        await callback_query.message.edit_text(HELP_MESSAGE, reply_markup=keyboard)
    
    # Answer the callback query to remove the loading indicator
    await callback_query.answer()
