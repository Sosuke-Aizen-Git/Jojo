import random
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from database import Chats
from config import WELCOME_MESSAGES

# Function to handle new members
@Client.on_chat_member_updated()
async def welcome_new_members(client: Client, chat_member_updated: ChatMemberUpdated):
    # Check if new member joined
    if not (chat_member_updated.new_chat_member and 
            chat_member_updated.new_chat_member.status in ["member", "restricted"] and
            (not chat_member_updated.old_chat_member or 
             chat_member_updated.old_chat_member.status in ["left", "banned"])):
        return
    
    # Get chat information
    chat_id = chat_member_updated.chat.id
    
    # Check if welcome messages are enabled for this chat
    chat_data = await Chats.find_one({"chat_id": chat_id})
    
    if not chat_data or not chat_data.get("welcome_enabled", True):
        return
    
    # Get new members
    new_member = chat_member_updated.new_chat_member.user
    
    # Skip if the user is a bot
    if new_member.is_bot:
        return
    
    # Get custom welcome message if it exists
    custom_welcome = chat_data.get("welcome_message") if chat_data else None
    
    if custom_welcome:
        welcome_text = custom_welcome
    else:
        # Use random welcome message from config
        welcome_text = random.choice(WELCOME_MESSAGES)
    
    # Replace placeholders in the welcome message
    welcome_text = welcome_text.replace("{user}", f"[{new_member.first_name}](tg://user?id={new_member.id})")
    welcome_text = welcome_text.replace("{chat}", chat_member_updated.chat.title)
    
    # Send welcome message
    await client.send_message(chat_id, welcome_text)


# Command to set custom welcome message
@Client.on_message(filters.command("setwelcome") & filters.group)
async def set_welcome_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to set a welcome message.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Check if there's a message to set
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            "Please provide a welcome message.\n\n"
            "You can use these placeholders:\n"
            "{user} - Mentions the new user\n"
            "{chat} - Shows the chat name\n\n"
            "Example: `/setwelcome Welcome {user} to {chat}!`"
        )
        return
    
    # Get the welcome message text
    if message.reply_to_message:
        welcome_text = message.reply_to_message.text or message.reply_to_message.caption or ""
    else:
        welcome_text = message.text.split(None, 1)[1]
    
    # Update the welcome message in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome_message": welcome_text, "welcome_enabled": True}},
        upsert=True
    )
    
    await message.reply_text("Star Platinum has set the new welcome message. ORA!")


# Command to reset welcome message to default
@Client.on_message(filters.command("resetwelcome") & filters.group)
async def reset_welcome_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to reset the welcome message.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Reset welcome message in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$unset": {"welcome_message": ""}, "$set": {"welcome_enabled": True}},
        upsert=True
    )
    
    await message.reply_text("The welcome message has been reset to default. ORAORAORA!")


# Command to disable welcome messages
@Client.on_message(filters.command("disablewelcome") & filters.group)
async def disable_welcome_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to disable welcome messages.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Disable welcome messages in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome_enabled": False}},
        upsert=True
    )
    
    await message.reply_text("Welcome messages have been disabled. Good grief...")


# Command to enable welcome messages
@Client.on_message(filters.command("enablewelcome") & filters.group)
async def enable_welcome_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to enable welcome messages.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Enable welcome messages in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome_enabled": True}},
        upsert=True
    )
    
    await message.reply_text("Welcome messages are now enabled. Star Platinum will greet new members! ORA!")
