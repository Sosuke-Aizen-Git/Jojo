import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API credentials from my.telegram.org
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jotarobot")

# Owner and sudo users (list of user IDs as integers)
OWNER_ID = int(os.getenv("OWNER_ID"))
SUDO_USERS = [int(user_id.strip()) for user_id in os.getenv("SUDO_USERS", "").split(",") if user_id.strip()]

# JoJo-themed greeting messages
WELCOME_MESSAGES = [
    "Yare yare daze... Welcome to the group, {mention}. Don't make me use Star Platinum on you.",
    "Good grief, another one joins. Welcome, {mention}. Try not to cause any trouble.",
    "ORA ORA ORA! Make way for {mention}, our newest member!",
    "Hmph. Welcome to the group, {mention}. Let's see if you're worth my time.",
    "Star Platinum welcomes you, {mention}. Just remember who's in charge here.",
    "So, {mention} has decided to join us. Good grief, this place keeps getting more crowded."
]

# JoJo-themed goodbye messages
GOODBYE_MESSAGES = [
    "Yare yare daze... {mention} couldn't handle it and left.",
    "Good grief. {mention} has decided to leave us. Probably for the best.",
    "ORA ORA OR-- Oh, {mention} is gone. Whatever.",
    "Hmph. {mention} has left the group. One less troublemaker to deal with.",
    "Star Platinum didn't even need to use force. {mention} left on their own.",
    "So, {mention} decided to leave. Good grief, not everyone can handle standing with us Stand users."
]

# Ban responses
BAN_RESPONSES = [
    "ORA ORA ORA ORA ORA! I've banned them with Star Platinum's power!",
    "Yare yare daze... Another troublemaker dealt with.",
    "Star Platinum: The World! Time has stopped for this user... permanently.",
    "Good grief. Had to use my Stand to remove this one.",
    "I can't ban them without getting closer? Fine, they're banned now.",
    "So it's the same type of Stand as troublemaking. They're banned."
]

# Unban responses
UNBAN_RESPONSES = [
    "Yare yare daze... I've unbanned them. Let's see if they've learned their lesson.",
    "Good grief. They get another chance. Don't waste it.",
    "Star Platinum has decided to show mercy. They're unbanned.",
    "Hmph. I've lifted their ban. Don't make me regret it.",
    "Fine, they can come back. But I'll be watching them...",
    "Star Platinum: The World! Time flows once more for this user."
]

# Mute responses
MUTE_RESPONSES = [
    "ORA ORA ORA! I've silenced them with Star Platinum!",
    "Yare yare daze... Now they can't make noise anymore.",
    "Star Platinum: The Silence! They can't speak now.",
    "Good grief. Had to shut this one up.",
    "I silenced them without even getting closer.",
    "So it's the same type of Stand as annoyance. They're muted now."
]

# Unmute responses
UNMUTE_RESPONSES = [
    "Yare yare daze... I've unmuted them. Let's see if they have anything useful to say.",
    "Good grief. They can speak again. Hope it's worth listening to.",
    "Star Platinum has decided they can talk again.",
    "Hmph. I've unmuted them. Don't make me regret it.",
    "Fine, they can speak now. But I'll be listening...",
    "Star Platinum: The World! Their voice returns."
]

# Promote responses
PROMOTE_RESPONSES = [
    "Good grief. I've promoted them to admin. Don't make me regret it.",
    "Star Platinum has deemed them worthy of admin powers.",
    "Yare yare daze... Another admin to help keep order.",
    "ORA ORA ORA! They've been promoted by Star Platinum's judgment!",
    "Hmph. They're an admin now. Let's see how they handle it.",
    "So it's the same type of Stand as leadership. They're promoted."
]

# Demote responses
DEMOTE_RESPONSES = [
    "Yare yare daze... I've demoted them. They weren't cut out for it.",
    "Good grief. Their admin days are over.",
    "Star Platinum has removed their admin status.",
    "ORA ORA ORA! Demoted faster than you can see Star Platinum move!",
    "Hmph. They're not an admin anymore. Couldn't handle the responsibility.",
    "So it's the same type of Stand as disappointment. They're demoted."
]

# Ping responses
PING_RESPONSES = [
    "ORA ORA ORA! Star Platinum is as fast as ever!",
    "Yare yare daze... I'm right here.",
    "Good grief. My Stand is faster than this ping, that's for sure.",
    "Star Platinum: The World! Even time stoppage is faster.",
    "Hmph. Star Platinum doesn't waste time with delays.",
    "So it's the same type of Stand as Speed. I'm always quick to respond."
]

# Purge responses
PURGE_RESPONSES = [
    "ORA ORA ORA! Star Platinum has erased all those messages!",
    "Yare yare daze... Cleaned up all that mess.",
    "Star Platinum: The Void! Those messages are gone now.",
    "Good grief. Had to clean up after everyone as usual.",
    "Hmph. Messages deleted faster than you can see Star Platinum move.",
    "So it's the same type of Stand as cleanup. Messages purged."
]

# Delete responses
DELETE_RESPONSES = [
    "ORA! Star Platinum deleted that with a single punch!",
    "Yare yare daze... That message is gone now.",
    "Star Platinum made that message disappear.",
    "Good grief. One less message to deal with.",
    "Hmph. Message deleted without even trying.",
    "So it's the same type of Stand as deletion. Message gone."
]

# Note saving responses
NOTE_RESPONSES = [
    "ORA ORA! Star Platinum has recorded this note!",
    "Yare yare daze... I've saved this note for future reference.",
    "Star Platinum: The Memory! This note is stored now.",
    "Good grief. Another note to remember.",
    "Hmph. Note saved faster than Star Platinum's punches.",
    "So it's the same type of Stand as memory. Note saved."
]

# Get note responses
GETNOTE_RESPONSES = [
    "ORA! Star Platinum has retrieved this note!",
    "Yare yare daze... Here's the note you wanted.",
    "Star Platinum: The Recall! Here's what you asked for.",
    "Good grief. You needed this note, right?",
    "Hmph. Note retrieved without breaking a sweat.",
    "So it's the same type of Stand as recall. Here's your note."
]

# Help responses for each command category
HELP_GENERAL = """
🌟 **General Commands**

• `/start` - Start the bot and get welcome message
• `/help` - Show this help message
• `/ping` - Check bot's response time
• `/stats` - Show bot statistics (admin only)
• `/info` - Get info about a user

Yare yare daze... These are my basic commands.
"""

HELP_ADMIN = """
⭐ **Admin Commands**

• `/ban` - Ban a user from the group
• `/unban` - Unban a user
• `/tban` - Temporarily ban a user
• `/mute` - Mute a user in the group
• `/unmute` - Unmute a user
• `/tmute` - Temporarily mute a user
• `/promote` - Promote a user to admin
• `/demote` - Demote an admin to regular user

Good grief... Use these powers wisely.
"""

HELP_UTILITY = """
💫 **Utility Commands**

• `/purge` - Delete multiple messages at once
• `/del` - Delete a specific message
• `/save` - Save a note for the group
• `/get` - Retrieve a saved note
• `/notes` - List all saved notes
• `/clear` - Delete a saved note

Star Platinum's powers extend beyond just punching.
"""

# Main help message combining all categories
HELP_MESSAGE = """
# Jotaro Kujo's Command Guide

Yare yare daze... Here are all my commands grouped by category. Select a category to see detailed commands:

🌟 **General** - Basic bot interaction commands
⭐ **Admin** - Group management and moderation
💫 **Utility** - Helpful features for your group

Use `/help [category]` to see specific commands in that category.

ORA ORA ORA! I'm ready to help maintain order in this group!
"""
