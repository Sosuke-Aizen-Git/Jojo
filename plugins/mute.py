import random
import re
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.errors import RPCError
from config import MUTE_RESPONSES, UNMUTE_RESPONSES

# Helper function to extract user and reason from command
async def extract_user_and_reason(client, message):
    user_id = None
    reason = None
    
    # Command format: /mute @username reason or /mute userid reason
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        reason = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    elif len(message.text.split()) > 1:
        entity = message.text.split()[1]
        
        # Check if it's a username (@username)
        if entity.startswith("@"):
            try:
                user = await client.get_users(entity)
                user_id = user.id
            except RPCError:
                await message.reply_text("I couldn't find that user.")
                return None, None
            
            if len(message.text.split()) > 2:
                reason = message.text.split(" ", 2)[2]
        
        # Check if it's a user ID
        elif entity.isdigit():
            user_id = int(entity)
            
            if len(message.text.split()) > 2:
                reason = message.text.split(" ", 2)[2]
        
        else:
            # Assume the rest of the message is the reason
            reason = message.text.split(" ", 1)[1]
    
    return user_id, reason


# Helper function to extract time from string like "5m", "1h", "30s"
def extract_time(time_string):
    if not time_string:
        return None
    
    time_regex = re.compile(r"(\d+)([smh])")
    match = time_regex.match(time_string)
    
    if not match:
        return None
    
    time_val, time_unit = match.groups()
    time_val = int(time_val)
    
    if time_unit == 's':
        return time_val
    elif time_unit == 'm':
        return time_val * 60
    elif time_unit == 'h':
        return time_val * 60 * 60


# Check if user has restrict permissions
async def has_restrict_permissions(client, message):
    if message.chat.type in ["private", "bot"]:
        return False
    
    # Get the sender's permissions
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status in ["creator", "administrator"]:
            if hasattr(chat_member, "privileges") and getattr(chat_member.privileges, "can_restrict_members", False):
                return True
            # For backward compatibility with older versions of pyrofork
            elif getattr(chat_member, "can_restrict_members", False):
                return True
    except RPCError:
        return False
    
    return False


# Mute command handler
@Client.on_message(filters.command("mute") & filters.group)
async def mute_command(client: Client, message: Message):
    # Check if user has permission to mute
    if not await has_restrict_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to mute users.")
        return
    
    # Check if bot has permission to mute
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_restrict_members", False) or 
             getattr(bot_chat_member, "can_restrict_members", False))):
        await message.reply_text("I don't have permission to mute users in this group. Give me restrict members rights first.")
        return
    
    # Extract user and reason
    user_id, reason = await extract_user_and_reason(client, message)
    
    if not user_id:
        await message.reply_text("I couldn't identify the user to mute. Try replying to their message or specifying their username/ID.")
        return
    
    # Don't allow muting the bot itself
    if user_id == (await client.get_me()).id:
        await message.reply_text("Heh, did you just try to make me mute myself? Not happening.")
        return
    
    # Don't allow muting admins
    try:
        user_member = await client.get_chat_member(message.chat.id, user_id)
        if user_member.status in ["creator", "administrator"]:
            await message.reply_text("Even Star Platinum can't mute an admin. Nice try though.")
            return
    except RPCError:
        await message.reply_text("There was an error checking the user's admin status.")
        return
    
    # Define mute permissions (can't send any messages)
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
    
    # All checks passed, mute the user
    try:
        await client.restrict_chat_member(message.chat.id, user_id, mute_permissions)
        
        # Get user info for the message
        try:
            muted_user = await client.get_users(user_id)
            user_mention = f"[{muted_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Send mute message with random Jotaro style response
        mute_response = random.choice(MUTE_RESPONSES)
        if reason:
            await message.reply_text(f"{mute_response}\n\n**User:** {user_mention}\n**Reason:** {reason}")
        else:
            await message.reply_text(f"{mute_response}\n\n**User:** {user_mention}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to mute user: {str(e)}")


# Unmute command handler
@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_command(client: Client, message: Message):
    # Check if user has permission to unmute
    if not await has_restrict_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to unmute users.")
        return
    
    # Check if bot has permission to unmute
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_restrict_members", False) or 
             getattr(bot_chat_member, "can_restrict_members", False))):
        await message.reply_text("I don't have permission to unmute users in this group. Give me restrict members rights first.")
        return
    
    # Extract user and reason
    user_id, reason = await extract_user_and_reason(client, message)
    
    if not user_id:
        await message.reply_text("I couldn't identify the user to unmute. Try replying to their message or specifying their username/ID.")
        return
    
    # Define unmute permissions (restore default permissions)
    unmute_permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_send_polls=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False
    )
    
    # All checks passed, unmute the user
    try:
        await client.restrict_chat_member(message.chat.id, user_id, unmute_permissions)
        
        # Get user info for the message
        try:
            unmuted_user = await client.get_users(user_id)
            user_mention = f"[{unmuted_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Send unmute message with random Jotaro style response
        unmute_response = random.choice(UNMUTE_RESPONSES)
        if reason:
            await message.reply_text(f"{unmute_response}\n\n**User:** {user_mention}\n**Reason:** {reason}")
        else:
            await message.reply_text(f"{unmute_response}\n\n**User:** {user_mention}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to unmute user: {str(e)}")


# Temporary mute command handler
@Client.on_message(filters.command("tmute") & filters.group)
async def temporary_mute_command(client: Client, message: Message):
    # Check if user has permission to mute
    if not await has_restrict_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to mute users.")
        return
    
    # Check if bot has permission to mute
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_restrict_members", False) or 
             getattr(bot_chat_member, "can_restrict_members", False))):
        await message.reply_text("I don't have permission to mute users in this group. Give me restrict members rights first.")
        return
    
    # Extract time, user and reason
    if len(message.command) < 3 and not message.reply_to_message:
        await message.reply_text("Not enough information provided. Format: `/tmute @username 5m reason` or reply to a message with `/tmute 5m reason`")
        return
    
    # If replying to a message
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        
        if len(message.command) < 2:
            await message.reply_text("You need to specify the mute duration (e.g., 5m, 1h, 30s).")
            return
        
        time_str = message.command[1]
        mute_time = extract_time(time_str)
        
        if not mute_time:
            await message.reply_text("Invalid time format. Use s for seconds, m for minutes, h for hours (e.g., 5m, 1h, 30s).")
            return
        
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else None
    
    # If mentioning a user
    else:
        if len(message.command) < 3:
            await message.reply_text("Not enough information provided. Format: `/tmute @username 5m reason`")
            return
        
        user_identifier = message.command[1]
        time_str = message.command[2]
        mute_time = extract_time(time_str)
        
        if not mute_time:
            await message.reply_text("Invalid time format. Use s for seconds, m for minutes, h for hours (e.g., 5m, 1h, 30s).")
            return
        
        # Get user ID from username or ID
        try:
            if user_identifier.startswith("@"):
                user = await client.get_users(user_identifier)
                user_id = user.id
            elif user_identifier.isdigit():
                user_id = int(user_identifier)
            else:
                await message.reply_text("Invalid user identifier. Use @username or user ID.")
                return
        except RPCError:
            await message.reply_text("I couldn't find that user.")
            return
        
        reason = " ".join(message.command[3:]) if len(message.command) > 3 else None
    
    # Don't allow muting the bot itself
    if user_id == (await client.get_me()).id:
        await message.reply_text("Heh, did you just try to make me mute myself? Not happening.")
        return
    
    # Don't allow muting admins
    try:
        user_member = await client.get_chat_member(message.chat.id, user_id)
        if user_member.status in ["creator", "administrator"]:
            await message.reply_text("Even Star Platinum can't mute an admin. Nice try though.")
            return
    except RPCError:
        await message.reply_text("There was an error checking the user's admin status.")
        return
    
    # Define mute permissions (can't send any messages)
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
    
    # Calculate unmute time
    unmute_time = int(time.time() + mute_time)
    
    # All checks passed, mute the user
    try:
        await client.restrict_chat_member(message.chat.id, user_id, mute_permissions, unmute_time)
        
        # Get user info for the message
        try:
            muted_user = await client.get_users(user_id)
            user_mention = f"[{muted_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Calculate readable time format
        time_dict = {"s": "seconds", "m": "minutes", "h": "hours"}
        time_unit = time_str[-1]
        time_value = time_str[:-1]
        readable_time = f"{time_value} {time_dict.get(time_unit, 'time units')}"
        
        # Send mute message with random Jotaro style response
        mute_response = random.choice(MUTE_RESPONSES)
        if reason:
            await message.reply_text(f"{mute_response}\n\n**User:** {user_mention}\n**Duration:** {readable_time}\n**Reason:** {reason}")
        else:
            await message.reply_text(f"{mute_response}\n\n**User:** {user_mention}\n**Duration:** {readable_time}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to temporarily mute user: {str(e)}")
