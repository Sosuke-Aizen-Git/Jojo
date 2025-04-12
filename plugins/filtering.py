import re
import random
from pyrofork import Client, filters
from pyrofork.types import Message
from pyrofork.errors import RPCError
from database import db

# Collection for filters
Filters = db.filters

# Helper function to check if user is admin
async def is_admin(client, message):
    if message.chat.type in ["private", "bot"]:
        return True
    
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return chat_member.status in ["administrator", "creator"]
    except RPCError:
        return False


# Add filter command handler
@Client.on_message(filters.command("filter") & ~filters.private)
async def add_filter_command(client: Client, message: Message):
    # Check if user is admin
    if not await is_admin(client, message):
        await message.reply_text("Yare yare daze... Only admins can add filters.")
        return
    
    # Get the filter keyword and content
    if len(message.command) < 2:
        await message.reply_text("You need to specify a filter keyword. Format: `/filter keyword content`")
        return
    
    keyword = message.command[1].lower()
    
    # Check if filter has content or is a reply
    if len(message.command) < 3 and not message.reply_to_message:
        await message.reply_text("You need to provide content for the filter or reply to a message.")
        return
    
    # Get filter content from reply or command
    if message.reply_to_message:
        if message.reply_to_message.text:
            filter_content = message.reply_to_message.text
        elif message.reply_to_message.caption:
            filter_content = message.reply_to_message.caption
        else:
            await message.reply_text("I can only save text messages as filters for now.")
            return
    else:
        filter_content = " ".join(message.command[2:])
    
    # Save the filter to the database
    await Filters.update_one(
        {"chat_id": message.chat.id, "keyword": keyword},
        {"$set": {"content": filter_content}},
        upsert=True
    )
    
    # Send success message
    await message.reply_text(f"Star Platinum has registered filter `{keyword}` successfully. ORA ORA ORA!")


# Remove filter command handler
@Client.on_message(filters.command("stop") & ~filters.private)
async def remove_filter_command(client: Client, message: Message):
    # Check if user is admin
    if not await is_admin(client, message):
        await message.reply_text("Yare yare daze... Only admins can remove filters.")
        return
    
    # Get the filter keyword
    if len(message.command) < 2:
        await message.reply_text("You need to specify a filter keyword. Format: `/stop keyword`")
        return
    
    keyword = message.command[1].lower()
    
    # Remove the filter from the database
    result = await Filters.delete_one({"chat_id": message.chat.id, "keyword": keyword})
    
    if result.deleted_count == 0:
        await message.reply_text(f"Filter `{keyword}` not found.")
        return
    
    # Send success message
    await message.reply_text(f"Yare yare daze... Filter `{keyword}` has been removed.")


# List filters command handler
@Client.on_message(filters.command("filters"))
async def list_filters_command(client: Client, message: Message):
    # Get all filters for the chat
    filters_cursor = Filters.find({"chat_id": message.chat.id})
    filters_list = await filters_cursor.to_list(length=None)
    
    if not filters_list:
        await message.reply_text("No filters saved in this chat.")
        return
    
    # Build filters list message
    filter_keywords = [f['keyword'] for f in filters_list]
    filter_list_text = "\n• ".join([f"`{keyword}`" for keyword in filter_keywords])
    
    await message.reply_text(f"**Filters in this chat:**\n\n• {filter_list_text}")


# Filter handler to respond to keywords
@Client.on_message(~filters.command & ~filters.private & ~filters.bot)
async def handle_filters(client: Client, message: Message):
    if not message.text:
        return
    
    # Get all filters for the chat
    filters_cursor = Filters.find({"chat_id": message.chat.id})
    filters_list = await filters_cursor.to_list(length=None)
    
    if not filters_list:
        return
    
    # Check if any filter keyword matches the message
    matched_filters = []
    
    for filter_item in filters_list:
        pattern = r'\b' + re.escape(filter_item['keyword']) + r'\b'
        if re.search(pattern, message.text.lower()):
            matched_filters.append(filter_item)
    
    # Respond with filter content for all matched filters
    for matched_filter in matched_filters:
        await message.reply_text(matched_filter['content'])
