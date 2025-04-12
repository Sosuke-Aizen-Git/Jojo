import random
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.errors import RPCError
from config import PROMOTE_RESPONSES, DEMOTE_RESPONSES

# Helper function to extract user from command
async def extract_user(client, message):
    user_id = None
    
    # Command format: /promote @username or /promote userid
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    elif len(message.text.split()) > 1:
        entity = message.text.split()[1]
        
        # Check if it's a username (@username)
        if entity.startswith("@"):
            try:
                user = await client.get_users(entity)
                user_id = user.id
            except RPCError:
                await message.reply_text("I couldn't find that user.")
                return None
        
        # Check if it's a user ID
        elif entity.isdigit():
            user_id = int(entity)
    
    return user_id


# Check if user has promote permissions
async def has_promote_permissions(client, message):
    if message.chat.type in ["private", "bot"]:
        return False
    
    # Get the sender's permissions
    try:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status == "creator":
            return True
        elif chat_member.status == "administrator":
            if hasattr(chat_member, "privileges") and getattr(chat_member.privileges, "can_promote_members", False):
                return True
            # For backward compatibility with older versions of pyrofork
            elif getattr(chat_member, "can_promote_members", False):
                return True
    except RPCError:
        return False
    
    return False


# Check bot's own permissions
async def get_bot_permissions(client, message):
    try:
        bot_chat_member = await client.get_chat_member(message.chat.id, (await client.get_me()).id)
        if bot_chat_member.status != "administrator":
            return None
        
        # Return the bot's privileges
        if hasattr(bot_chat_member, "privileges"):
            return bot_chat_member.privileges
        else:
            # For backward compatibility, create a privileges object with the available fields
            privileges = {}
            for field in [
                "can_change_info", "can_delete_messages", "can_restrict_members",
                "can_invite_users", "can_pin_messages", "can_promote_members",
                "can_manage_chat", "can_manage_video_chats"
            ]:
                if hasattr(bot_chat_member, field):
                    privileges[field] = getattr(bot_chat_member, field)
            return privileges
    except RPCError:
        return None


# Promote command handler
@Client.on_message(filters.command("promote") & filters.group)
async def promote_command(client: Client, message: Message):
    # Check if user has permission to promote
    if not await has_promote_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to promote users.")
        return
    
    # Check if bot has permission to promote
    bot_privileges = await get_bot_permissions(client, message)
    if not bot_privileges or not (hasattr(bot_privileges, "can_promote_members") and bot_privileges.can_promote_members):
        await message.reply_text("I don't have permission to promote users in this group. Give me promote members rights first.")
        return
    
    # Extract user
    user_id = await extract_user(client, message)
    
    if not user_id:
        await message.reply_text("I couldn't identify the user to promote. Try replying to their message or specifying their username/ID.")
        return
    
    # Don't allow promoting the bot itself
    if user_id == (await client.get_me()).id:
        await message.reply_text("I can't promote myself. I need someone else to do that.")
        return
    
    # Check if user is already an admin
    try:
        user_member = await client.get_chat_member(message.chat.id, user_id)
        if user_member.status in ["creator", "administrator"]:
            await message.reply_text("This user is already an administrator.")
            return
    except RPCError:
        await message.reply_text("There was an error checking the user's admin status.")
        return
    
    # Create privileges based on bot's own privileges
    privileges = ChatPrivileges(
        can_change_info=getattr(bot_privileges, "can_change_info", False),
        can_delete_messages=getattr(bot_privileges, "can_delete_messages", False),
        can_restrict_members=getattr(bot_privileges, "can_restrict_members", False),
        can_invite_users=getattr(bot_privileges, "can_invite_users", False),
        can_pin_messages=getattr(bot_privileges, "can_pin_messages", False),
        can_manage_chat=getattr(bot_privileges, "can_manage_chat", False),
        can_manage_video_chats=getattr(bot_privileges, "can_manage_video_chats", False),
        # Don't give promote_members permission regardless of bot's own permissions
        can_promote_members=False,
        # Don't give anonymous permission regardless of bot's own permissions
        is_anonymous=False
    )
    
    # All checks passed, promote the user
    try:
        await client.promote_chat_member(message.chat.id, user_id, privileges)
        
        # Get user info for the message
        try:
            promoted_user = await client.get_users(user_id)
            user_mention = f"[{promoted_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Send promote message with random Jotaro style response
        promote_response = random.choice(PROMOTE_RESPONSES)
        await message.reply_text(f"{promote_response}\n\n**User:** {user_mention}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to promote user: {str(e)}")


# Demote command handler
@Client.on_message(filters.command("demote") & filters.group)
async def demote_command(client: Client, message: Message):
    # Check if user has permission to demote
    if not await has_promote_permissions(client, message):
        await message.reply_text("Yare yare daze... You don't have permission to demote users.")
        return
    
    # Check if bot has permission to demote
    bot_privileges = await get_bot_permissions(client, message)
    if not bot_privileges or not (hasattr(bot_privileges, "can_promote_members") and bot_privileges.can_promote_members):
        await message.reply_text("I don't have permission to demote users in this group. Give me promote members rights first.")
        return
    
    # Extract user
    user_id = await extract_user(client, message)
    
    if not user_id:
        await message.reply_text("I couldn't identify the user to demote. Try replying to their message or specifying their username/ID.")
        return
    
    # Don't allow demoting the bot itself
    if user_id == (await client.get_me()).id:
        await message.reply_text("I can't demote myself. Nice try though.")
        return
    
    # Check if user is an admin
    try:
        user_member = await client.get_chat_member(message.chat.id, user_id)
        if user_member.status == "creator":
            await message.reply_text("I can't demote the group creator. Even Star Platinum has its limits.")
            return
        elif user_member.status != "administrator":
            await message.reply_text("This user is not an administrator.")
            return
    except RPCError:
        await message.reply_text("There was an error checking the user's admin status.")
        return
    
    # Create privileges with all permissions set to False
    privileges = ChatPrivileges(
        can_change_info=False,
        can_delete_messages=False,
        can_restrict_members=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_manage_chat=False,
        can_manage_video_chats=False,
        can_promote_members=False,
        is_anonymous=False
    )
    
    # All checks passed, demote the user
    try:
        await client.promote_chat_member(message.chat.id, user_id, privileges)
        
        # Get user info for the message
        try:
            demoted_user = await client.get_users(user_id)
            user_mention = f"[{demoted_user.first_name}](tg://user?id={user_id})"
        except:
            user_mention = f"User {user_id}"
        
        # Send demote message with random Jotaro style response
        demote_response = random.choice(DEMOTE_RESPONSES)
        await message.reply_text(f"{demote_response}\n\n**User:** {user_mention}")
            
    except RPCError as e:
        await message.reply_text(f"Failed to demote user: {str(e)}")
