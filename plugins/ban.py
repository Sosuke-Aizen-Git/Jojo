import random
import re
import time
from datetime import datetime, timedelta
from pyrofork import Client, filters
from pyrofork.types import Message, ChatPermissions, ChatMemberUpdated
from pyrofork.errors import RPCError
from config import BAN_RESPONSES, UNBAN_RESPONSES

# Helper function to extract user and reason from command
async def extract_user_and_reason(client, message):
    user_id = None
    reason = None
    
    # Command format: /ban @username reason or /ban userid reason
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


# Check if user has ban permissions
async def has_ban_permissions(client, message):
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


# Ban command handler
@Client.on_message(filters.command("ban") & filters.group)
async def ban_command(client: Client, message: Message):
    # Check if user has permission to ban
    if not await has_ban_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to ban users.")
        return
    
    # Check if bot has permission to ban
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_restrict_members", False) or 
             getattr(bot_chat_member, "can_restrict_members", False))):
        await message.reply_text("I don't have permission to ban users in this group. Give me ban rights first.")
        return
    
    # Extract user and reason
    user_id, reason = await extract_user_and_reason(client, message)
    
    if not user_id:
        await message.reply_text("I couldn't identify the user to ban. Try replying to their message or specifying their username/ID.")
        return
    
    # Don't allow banning the bot itself
    if user_id == (await client.get_me()).id:
        await message.reply_text("Heh, did you just try to make me ban myself? Not happening.")
        return
    
    # Don't allow banning admins
    try:
        user_member = await client.get_chat_member(message.chat.id, user_id)
        if user_member.status in ["creator", "administrator"]:
            await message.reply_text("Even Star Platinum can't ban an admin. Nice try though.")
            return
    except RPCError:
        await message.reply_text("There was an error checking the user's admin status.")
        return
    
    # All checks passed, ban the user
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        
        # Get user info for the message
        try:
            banned_user = await client.get_users(user_id)
            user_mention = f"[{banned_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Send ban message with random Jotaro style response
        ban_response = random.choice(BAN_RESPONSES)
        if reason:
            await message.reply_text(f"{ban_response}\n\n**User:** {user_mention}\n**Reason:** {reason}")
        else:
            await message.reply_text(f"{ban_response}\n\n**User:** {user_mention}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to ban user: {str(e)}")


# Unban command handler
@Client.on_message(filters.command("unban") & filters.group)
async def unban_command(client: Client, message: Message):
    # Check if user has permission to unban
    if not await has_ban_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to unban users.")
        return
    
    # Check if bot has permission to unban
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_restrict_members", False) or 
             getattr(bot_chat_member, "can_restrict_members", False))):
        await message.reply_text("I don't have permission to unban users in this group. Give me ban rights first.")
        return
    
    # Extract user and reason
    user_id, reason = await extract_user_and_reason(client, message)
    
    if not user_id:
        await message.reply_text("I couldn't identify the user to unban. Try specifying their username/ID.")
        return
    
    # All checks passed, unban the user
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        
        # Get user info for the message
        try:
            unbanned_user = await client.get_users(user_id)
            user_mention = f"[{unbanned_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Send unban message with random Jotaro style response
        unban_response = random.choice(UNBAN_RESPONSES)
        if reason:
            await message.reply_text(f"{unban_response}\n\n**User:** {user_mention}\n**Reason:** {reason}")
        else:
            await message.reply_text(f"{unban_response}\n\n**User:** {user_mention}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to unban user: {str(e)}")

# Temporary ban command handler
@Client.on_message(filters.command("tban") & filters.group)
async def temporary_ban_command(client: Client, message: Message):
    # Check if user has permission to ban
    if not await has_ban_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to ban users.")
        return
    
    # Check if bot has permission to ban
    bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
    if not (bot_chat_member.status == "administrator" and 
            (hasattr(bot_chat_member, "privileges") and getattr(bot_chat_member.privileges, "can_restrict_members", False) or 
             getattr(bot_chat_member, "can_restrict_members", False))):
        await message.reply_text("I don't have permission to ban users in this group. Give me ban rights first.")
        return
    
    # Extract time, user and reason
    if len(message.command) < 3 and not message.reply_to_message:
        await message.reply_text("Not enough information provided. Format: `/tban @username 5m reason` or reply to a message with `/tban 5m reason`")
        return
    
    # If replying to a message
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        
        if len(message.command) < 2:
            await message.reply_text("You need to specify the ban duration (e.g., 5m, 1h, 30s).")
            return
        
        time_str = message.command[1]
        ban_time = extract_time(time_str)
        
        if not ban_time:
            await message.reply_text("Invalid time format. Use s for seconds, m for minutes, h for hours (e.g., 5m, 1h, 30s).")
            return
        
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else None
    
    # If mentioning a user
    else:
        if len(message.command) < 3:
            await message.reply_text("Not enough information provided. Format: `/tban @username 5m reason`")
            return
        
        user_identifier = message.command[1]
        time_str = message.command[2]
        ban_time = extract_time(time_str)
        
        if not ban_time:
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
    
    # Don't allow banning the bot itself
    if user_id == (await client.get_me()).id:
        await message.reply_text("Heh, did you just try to make me ban myself? Not happening.")
        return
    
    # Don't allow banning admins
    try:
        user_member = await client.get_chat_member(message.chat.id, user_id)
        if user_member.status in ["creator", "administrator"]:
            await message.reply_text("Even Star Platinum can't ban an admin. Nice try though.")
            return
    except RPCError:
        await message.reply_text("There was an error checking the user's admin status.")
        return
    
    # Calculate unban time
    unban_time = int(time.time() + ban_time)
    
    # All checks passed, ban the user
    try:
        await client.ban_chat_member(message.chat.id, user_id, unban_time)
        
        # Get user info for the message
        try:
            banned_user = await client.get_users(user_id)
            user_mention = f"[{banned_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Calculate readable time format
        time_dict = {"s": "seconds", "m": "minutes", "h": "hours"}
        time_unit = time_str[-1]
        time_value = time_str[:-1]
        readable_time = f"{time_value} {time_dict.get(time_unit, 'time units')}"
        
        # Send ban message with random Jotaro style response
        ban_response = random.choice(BAN_RESPONSES)
        if reason:
            await message.reply_text(f"{ban_response}\n\n**User:** {user_mention}\n**Duration:** {readable_time}\n**Reason:** {reason}")
        else:
            await message.reply_text(f"{ban_response}\n\n**User:** {user_mention}\n**Duration:** {readable_time}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to temporarily ban user: {str(e)}")
