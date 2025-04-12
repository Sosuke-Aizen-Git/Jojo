import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import RPCError
from database import db
from config import NOTE_RESPONSES, GETNOTE_RESPONSES

# Collection for notes
Notes = db.notes

# Helper function to check if user is admin
async def is_admin(client, message):
    if message.chat.type in ["private", "bot"]:
        return True
    
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return chat_member.status in ["administrator", "creator"]
    except RPCError:
        return False


# Save note command handler
@Client.on_message(filters.command("save") & ~filters.private)
async def save_note_command(client: Client, message: Message):
    # Check if user is admin
    if not await is_admin(client, message):
        await message.reply_text("Yare yare daze... Only admins can save notes.")
        return
    
    # Get the note name and content
    if len(message.command) < 2:
        await message.reply_text("You need to specify a note name. Format: `/save notename content`")
        return
    
    note_name = message.command[1].lower()
    
    # Check if note has content or is a reply
    if len(message.command) < 3 and not message.reply_to_message:
        await message.reply_text("You need to provide content for the note or reply to a message.")
        return
    
    # Get note content from reply or command
    if message.reply_to_message:
        if message.reply_to_message.text:
            note_content = message.reply_to_message.text
        elif message.reply_to_message.caption:
            note_content = message.reply_to_message.caption
        else:
            await message.reply_text("I can only save text messages as notes for now.")
            return
    else:
        note_content = " ".join(message.command[2:])
    
    # Save the note to the database
    await Notes.update_one(
        {"chat_id": message.chat.id, "note_name": note_name},
        {"$set": {"content": note_content}},
        upsert=True
    )
    
    # Send success message
    note_response = random.choice(NOTE_RESPONSES)
    await message.reply_text(f"{note_response}\n\nNote `{note_name}` saved successfully.")


# Get note command handler
@Client.on_message(filters.command("get"))
async def get_note_command(client: Client, message: Message):
    # Get the note name
    if len(message.command) < 2:
        await message.reply_text("You need to specify a note name. Format: `/get notename`")
        return
    
    note_name = message.command[1].lower()
    
    # Get the note from the database
    note = await Notes.find_one({"chat_id": message.chat.id, "note_name": note_name})
    
    if not note:
        await message.reply_text(f"Note `{note_name}` not found.")
        return
    
    # Send the note content
    getnote_response = random.choice(GETNOTE_RESPONSES)
    await message.reply_text(f"{getnote_response}\n\n**Note:** `{note_name}`\n\n{note['content']}")


# Notes command handler to list all notes
@Client.on_message(filters.command("notes"))
async def notes_command(client: Client, message: Message):
    # Get all notes for the chat
    notes_cursor = Notes.find({"chat_id": message.chat.id})
    notes_list = await notes_cursor.to_list(length=None)
    
    if not notes_list:
        await message.reply_text("No notes saved in this chat.")
        return
    
    # Build notes list message
    note_names = [note["note_name"] for note in notes_list]
    note_list_text = "\n• ".join([f"`{name}`" for name in note_names])
    
    await message.reply_text(f"**Notes in this chat:**\n\n• {note_list_text}\n\nUse `/get notename` to view a note.")


# Delete note command handler
@Client.on_message(filters.command("clear") & ~filters.private)
async def delete_note_command(client: Client, message: Message):
    # Check if user is admin
    if not await is_admin(client, message):
        await message.reply_text("Yare yare daze... Only admins can delete notes.")
        return
    
    # Get the note name
    if len(message.command) < 2:
        await message.reply_text("You need to specify a note name. Format: `/clear notename`")
        return
    
    note_name = message.command[1].lower()
    
    # Delete the note from the database
    result = await Notes.delete_one({"chat_id": message.chat.id, "note_name": note_name})
    
    if result.deleted_count == 0:
        await message.reply_text(f"Note `{note_name}` not found.")
        return
    
    # Send success message
    await message.reply_text(f"Note `{note_name}` deleted successfully.")


# Shortcut for getting notes using #notename
@Client.on_message(filters.regex(r"^#([a-zA-Z0-9_]+)") & ~filters.private)
async def note_hashtag(client: Client, message: Message):
    # Extract note name from hashtag
    match = message.text.strip()
    if not match.startswith('#'):
        return
    
    note_name = match[1:].lower()
    
    # Get the note from the database
    note = await Notes.find_one({"chat_id": message.chat.id, "note_name": note_name})
    
    if not note:
        return
    
    # Send the note content
    getnote_response = random.choice(GETNOTE_RESPONSES)
    await message.reply_text(f"{getnote_response}\n\n**Note:** `{note_name}`\n\n{note['content']}")
