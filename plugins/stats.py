import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from database import Users, Chats
from config import OWNER_ID, SUDO_USERS

# Global variable to store bot start time
START_TIME = time.time()

# Helper function to format time delta
def format_time_delta(td):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts)


# Stats command handler
@Client.on_message(filters.command("stats") & (filters.user(OWNER_ID) | filters.user(SUDO_USERS)))
async def stats_command(client: Client, message: Message):
    # Only allow stats command for owner and sudo users
    if message.from_user.id not in [OWNER_ID] + SUDO_USERS:
        await message.reply_text("Yare yare daze... This command is only for my Stand users.")
        return
    
    # Get uptime
    uptime = timedelta(seconds=int(time.time() - START_TIME))
    formatted_uptime = format_time_delta(uptime)
    
    # Get user count from database
    total_users = await Users.count_documents({})
    
    # Get chat count from database
    total_chats = await Chats.count_documents({})
    
    # Count group chats
    group_chats = await Chats.count_documents({"type": {"$in": ["group", "supergroup"]}})
    
    # Count private chats
    private_chats = await Chats.count_documents({"type": "private"})
    
    # Count channel chats
    channel_chats = await Chats.count_documents({"type": "channel"})
    
    # Format stats message
    stats_text = (
        "# Jotaro Bot Stats\n\n"
        f"**Uptime:** {formatted_uptime}\n"
        f"**Total Users:** {total_users:,}\n"
        f"**Total Chats:** {total_chats:,}\n"
        f"**└ Groups:** {group_chats:,}\n"
        f"**└ Private Chats:** {private_chats:,}\n"
        f"**└ Channels:** {channel_chats:,}\n\n"
        "Ora ora ora! These are my current stats."
    )
    
    await message.reply_text(stats_text)
