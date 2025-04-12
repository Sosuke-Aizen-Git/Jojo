import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError
from config import PURGE_RESPONSES, DELETE_RESPONSES

# Helper function to check delete permissions
async def has_delete_permissions(client, message):
    if message.chat.type in ["private", "bot"]:
        # In private chats, users can delete their own messages
        return True
    
    # Get the sender's permissions
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status in ["creator", "administrator"]:
            if hasattr(chat_member, "privileges") and getattr(chat_member.privileges, "can_delete_messages", False):
                return True
            # For backward compatibility with older versions of pyrofork
            elif getattr(chat_member, "can_delete_messages", False):
                return True
    except RPCError:
        return False
    
    return False


# Purge command handler
@Client.on_message(filters.command("purge") & ~filters.private)
async def purge_command(client: Client, message: Message):
    # Check if user has permission to delete messages
    if not await has_delete_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to delete messages.")
        return
    
    # Check if bot has permission to delete messages
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_delete_messages", False) or 
             getattr(bot_chat_member, "can_delete_messages", False))):
        await message.reply_text("I don't have permission to delete messages in this group. Give me delete messages rights first.")
        return
    
    # Check if the command is a reply
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to purge from.")
        return
    
    # Get message IDs to delete
    start_message_id = message.reply_to_message.id
    end_message_id = message.id
    
    # Count and delete messages
    deleted_count = 0
    for message_id in range(start_message_id, end_message_id + 1):
        try:
            await client.delete_messages(message.chat.id, message_id)
            deleted_count += 1
        except RPCError:
            pass
        
        # Add a small delay to avoid hitting rate limits
        await asyncio.sleep(0.01)
    
    # Send success message
    if deleted_count > 0:
        purge_response = random.choice(PURGE_RESPONSES)
        success_message = await message.reply_text(f"{purge_response}\n\n**Messages Deleted:** {deleted_count}")
        
        # Delete the success message after 3 seconds
        await asyncio.sleep(3)
        await success_message.delete()
    else:
        await message.reply_text("No messages were deleted. I might not have permission to delete some messages.")


# Delete command handler
@Client.on_message(filters.command("del") & ~filters.private)
async def delete_command(client: Client, message: Message):
    # Check if user has permission to delete messages
    if not await has_delete_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to delete messages.")
        return
    
    # Check if bot has permission to delete messages
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_delete_messages", False) or 
             getattr(bot_chat_member, "can_delete_messages", False))):
        await message.reply_text("I don't have permission to delete messages in this group. Give me delete messages rights first.")
        return
    
    # Check if the command is a reply
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to delete it.")
        return
    
    # Delete the replied message
    try:
        await message.reply_to_message.delete()
        delete_response = random.choice(DELETE_RESPONSES)
        success_message = await message.reply_text(delete_response)
        
        # Delete the command message
        await message.delete()
        
        # Delete the success message after 3 seconds
        await asyncio.sleep(3)
        await success_message.delete()
    except RPCError as e:
        await message.reply_text(f"Failed to delete message: {str(e)}")
