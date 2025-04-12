import re
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError
from database import db

# Collection for blacklisted words
Blacklist = db.blacklist

# Helper function to check if user is admin
async def is_admin(client, message):
    if message.chat.type in ["private", "bot"]:
        return True
    
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return chat_member.status in ["administrator", "creator"]
    except RPCError:
        return False


# Add blacklist word command handler
@Client.on_message(filters.command("blacklist") & ~filters.private)
async def add_blacklist_command(client: Client, message: Message):
    # Check if user is admin
    if not await is_admin(client, message):
        await message.reply_text("Yare yare daze... Only admins can add blacklisted words.")
        return
    
    # Get the blacklist word(s)
    if len(message.command) < 2:
        await message.reply_text("You need to specify word(s) to blacklist. Format: `/blacklist word1 word2 ...`")
        return
    
    words = [word.lower() for word in message.command[1:]]
    added_words = []
    
    # Add each word to the blacklist in the database
    for word in words:
        # Check if word is already blacklisted
        existing = await Blacklist.find_one({"chat_id": message.chat.id, "word": word})
        if existing:
            continue
        
        # Add word to blacklist
        await Blacklist.insert_one({"chat_id": message.chat.id, "word": word})
        added_words.append(word)
    
    # Send success message
    if added_words:
        words_list = ", ".join([f"`{word}`" for word in added_words])
        await message.reply_text(f"ORA ORA ORA! Added {len(added_words)} word(s) to the blacklist: {words_list}")
    else:
        await message.reply_text("Yare yare daze... All those words are already blacklisted.")


# Remove blacklist word command handler
@Client.on_message(filters.command("unblacklist") & ~filters.private)
async def remove_blacklist_command(client: Client, message: Message):
    # Check if user is admin
    if not await is_admin(client, message):
        await message.reply_text("Yare yare daze... Only admins can remove blacklisted words.")
        return
    
    # Get the blacklist word(s)
    if len(message.command) < 2:
        await message.reply_text("You need to specify word(s) to remove from blacklist. Format: `/unblacklist word1 word2 ...`")
        return
    
    words = [word.lower() for word in message.command[1:]]
    removed_words = []
    
    # Remove each word from the blacklist in the database
    for word in words:
        result = await Blacklist.delete_one({"chat_id": message.chat.id, "word": word})
        if result.deleted_count > 0:
            removed_words.append(word)
    
    # Send success message
    if removed_words:
        words_list = ", ".join([f"`{word}`" for word in removed_words])
        await message.reply_text(f"Good grief. Removed {len(removed_words)} word(s) from the blacklist: {words_list}")
    else:
        await message.reply_text("Yare yare daze... None of those words were blacklisted.")


# List blacklisted words command handler
@Client.on_message(filters.command("blacklists"))
async def list_blacklist_command(client: Client, message: Message):
    # Check if user is admin
    if not await is_admin(client, message):
        await message.reply_text("Yare yare daze... Only admins can view blacklisted words.")
        return
    
    # Get all blacklisted words for the chat
    blacklist_cursor = Blacklist.find({"chat_id": message.chat.id})
    blacklist = await blacklist_cursor.to_list(length=None)
    
    if not blacklist:
        await message.reply_text("No words are blacklisted in this chat.")
        return
    
    # Build blacklist message
    words = [item['word'] for item in blacklist]
    words_list = "\n• ".join([f"`{word}`" for word in words])
    
    await message.reply_text(f"**Blacklisted words in this chat:**\n\n• {words_list}")


# Handler for blacklisted words in messages
@Client.on_message(~filters.command & ~filters.private & ~filters.bot)
async def handle_blacklist(client: Client, message: Message):
    if not message.text:
        return
    
    # Check if message sender is admin (admins bypass blacklist)
    if await is_admin(client, message):
        return
    
    # Get all blacklisted words for the chat
    blacklist_cursor = Blacklist.find({"chat_id": message.chat.id})
    blacklist = await blacklist_cursor.to_list(length=None)
    
    if not blacklist:
        return
    
    # Check if message contains any blacklisted word
    text = message.text.lower()
    for item in blacklist:
        pattern = r'\b' + re.escape(item['word']) + r'\b'
        if re.search(pattern, text):
            # Delete the message
            try:
                await message.delete()
                # Notify user about the deletion
                warn_msg = await message.reply_text(
                    f"ORA ORA ORA! Star Platinum has detected a blacklisted word from {message.from_user.mention}.\n\n"
                    f"Yare yare daze... Don't use blacklisted words in this group."
                )
                
                # Delete the warning message after 5 seconds
                time.sleep(5)
                await warn_msg.delete()
            except RPCError:
                pass
            
            # Only need to delete once even if multiple blacklisted words found
            break
