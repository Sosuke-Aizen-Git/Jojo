import time
import asyncio
from collections import defaultdict
from pyrofork import Client, filters
from pyrofork.types import Message, ChatPermissions
from pyrofork.errors import RPCError
from database import Chats

# Default antiflood settings
DEFAULT_FLOOD_LIMIT = 5  # messages
DEFAULT_FLOOD_TIME = 5   # seconds
DEFAULT_FLOOD_MODE = "mute"
DEFAULT_FLOOD_DURATION = 600  # seconds (10 minutes)

# Store user message counts: {chat_id: {user_id: [time1, time2, ...]}}
FLOOD_CACHE = defaultdict(lambda: defaultdict(list))

# Check for flood
async def is_flooding(chat_id, user_id, flood_limit, flood_time):
    # Clean up old messages first
    current_time = time.time()
    FLOOD_CACHE[chat_id][user_id] = [
        msg_time for msg_time in FLOOD_CACHE[chat_id][user_id]
        if current_time - msg_time <= flood_time
    ]
    
    # Add current message time
    FLOOD_CACHE[chat_id][user_id].append(current_time)
    
    # Check if the number of messages in the time window exceeds the limit
    return len(FLOOD_CACHE[chat_id][user_id]) > flood_limit


# Handle flooding
async def handle_flood(client, message, mode, duration):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if mode == "mute":
        mute_permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_send_polls=False,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False
        )
        
        try:
            # Mute the user for the specified duration
            await client.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=mute_permissions,
                until_date=int(time.time() + duration)
            )
            
            await message.reply_text(
                f"Yare yare daze... Star Platinum has muted user for flooding!\n"
                f"User: [User](tg://user?id={user_id})\n"
                f"Duration: {duration // 60} minute(s)"
            )
            
        except RPCError as e:
            await message.reply_text(f"Failed to mute user: {str(e)}")
    
    elif mode == "kick":
        try:
            # Kick the user
            await client.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await client.unban_chat_member(chat_id=chat_id, user_id=user_id)
            
            await message.reply_text(
                f"ORA ORA ORA! Star Platinum has kicked user for flooding!\n"
                f"User: [User](tg://user?id={user_id})"
            )
            
        except RPCError as e:
            await message.reply_text(f"Failed to kick user: {str(e)}")
    
    elif mode == "ban":
        try:
            # Ban the user for the specified duration
            await client.ban_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                until_date=int(time.time() + duration)
            )
            
            await message.reply_text(
                f"ORAORAORA! Star Platinum has banned user for flooding!\n"
                f"User: [User](tg://user?id={user_id})\n"
                f"Duration: {duration // 60} minute(s)"
            )
            
        except RPCError as e:
            await message.reply_text(f"Failed to ban user: {str(e)}")
    
    # Clear the user's message history after taking action
    FLOOD_CACHE[chat_id][user_id] = []


# Handle incoming messages to check for flooding
@Client.on_message(filters.group & ~filters.service & ~filters.me & ~filters.bot)
async def check_flood(client: Client, message: Message):
    # Skip messages without a proper user
    if not message.from_user:
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Check if the user is an admin
    try:
        user_member = await client.get_chat_member(chat_id, user_id)
        if user_member.status in ["creator", "administrator"]:
            return  # Skip flood check for admins
    except RPCError:
        pass  # If we can't check admin status, continue with flood protection
    
    # Get antiflood settings for this chat
    chat_data = await Chats.find_one({"chat_id": chat_id})
    
    # If no settings or antiflood disabled, use defaults
    if not chat_data or not chat_data.get("antiflood_enabled", False):
        return
    
    flood_limit = chat_data.get("flood_limit", DEFAULT_FLOOD_LIMIT)
    flood_time = chat_data.get("flood_time", DEFAULT_FLOOD_TIME)
    flood_mode = chat_data.get("flood_mode", DEFAULT_FLOOD_MODE)
    flood_duration = chat_data.get("flood_duration", DEFAULT_FLOOD_DURATION)
    
    # Check if user is flooding
    if await is_flooding(chat_id, user_id, flood_limit, flood_time):
        await handle_flood(client, message, flood_mode, flood_duration)


# Command to set antiflood settings
@Client.on_message(filters.command("setflood") & filters.group)
async def set_flood_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to set antiflood settings.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Check command arguments
    if len(message.command) < 2:
        await message.reply_text(
            "Please provide the flood limit.\n\n"
            "Usage: `/setflood [number]`\n"
            "Example: `/setflood 5`"
        )
        return
    
    try:
        flood_limit = int(message.command[1])
        if flood_limit < 3:
            await message.reply_text("Flood limit should be at least 3.")
            return
        if flood_limit > 20:
            await message.reply_text("Flood limit should not exceed 20.")
            return
    except ValueError:
        await message.reply_text("Flood limit should be a number.")
        return
    
    # Update flood settings in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"flood_limit": flood_limit, "antiflood_enabled": True}},
        upsert=True
    )
    
    await message.reply_text(f"Star Platinum has set the flood limit to {flood_limit} messages. ORA!")


# Command to set antiflood mode
@Client.on_message(filters.command("setfloodmode") & filters.group)
async def set_flood_mode_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to set antiflood mode.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Check command arguments
    if len(message.command) < 2:
        await message.reply_text(
            "Please provide the flood mode.\n\n"
            "Available modes: `mute`, `kick`, `ban`\n"
            "Usage: `/setfloodmode [mode]`\n"
            "Example: `/setfloodmode mute`"
        )
        return
    
    mode = message.command[1].lower()
    if mode not in ["mute", "kick", "ban"]:
        await message.reply_text("Invalid mode. Available modes: `mute`, `kick`, `ban`")
        return
    
    # Update flood mode in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"flood_mode": mode, "antiflood_enabled": True}},
        upsert=True
    )
    
    await message.reply_text(f"Star Platinum has set the flood mode to {mode}. ORAORAORA!")


# Command to set flood duration (for mute/ban)
@Client.on_message(filters.command("setfloodduration") & filters.group)
async def set_flood_duration_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to set flood duration.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Check command arguments
    if len(message.command) < 2:
        await message.reply_text(
            "Please provide the duration in minutes.\n\n"
            "Usage: `/setfloodduration [minutes]`\n"
            "Example: `/setfloodduration 10`"
        )
        return
    
    try:
        duration_minutes = int(message.command[1])
        if duration_minutes < 1:
            await message.reply_text("Duration should be at least 1 minute.")
            return
        if duration_minutes > 1440:  # 24 hours max
            await message.reply_text("Duration should not exceed 1440 minutes (24 hours).")
            return
    except ValueError:
        await message.reply_text("Duration should be a number in minutes.")
        return
    
    # Convert minutes to seconds
    duration_seconds = duration_minutes * 60
    
    # Update flood duration in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"flood_duration": duration_seconds, "antiflood_enabled": True}},
        upsert=True
    )
    
    await message.reply_text(f"Star Platinum has set the flood punishment duration to {duration_minutes} minute(s). ORA!")


# Command to disable antiflood
@Client.on_message(filters.command("disableflood") & filters.group)
async def disable_flood_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to disable antiflood.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Disable antiflood in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"antiflood_enabled": False}},
        upsert=True
    )
    
    await message.reply_text("Antiflood protection has been disabled. Good grief...")


# Command to enable antiflood
@Client.on_message(filters.command("enableflood") & filters.group)
async def enable_flood_command(client: Client, message: Message):
    # Check if user is an admin
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ["creator", "administrator"]:
            await message.reply_text("Yare yare daze... You need to be an admin to enable antiflood.")
            return
    except Exception as e:
        await message.reply_text(f"Error checking permissions: {str(e)}")
        return
    
    # Enable antiflood in the database
    chat_id = message.chat.id
    await Chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"antiflood_enabled": True}},
        upsert=True
    )
    
    await message.reply_text("Antiflood protection is now enabled. Star Platinum will protect against spammers! ORA!")
