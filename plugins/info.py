from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated
from pyrogram.errors import RPCError

# Helper function to extract user from command
async def extract_user(client, message):
    user_id = None
    user_first_name = None
    
    # Command format: /info @username or /info userid
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        entity = message.command[1]
        
        # Check if it's a username (@username)
        if entity.startswith("@"):
            try:
                user = await client.get_users(entity)
                user_id = user.id
                user_first_name = user.first_name
            except RPCError:
                await message.reply_text("I couldn't find that user.")
                return None, None
        
        # Check if it's a user ID
        elif entity.isdigit():
            user_id = int(entity)
            try:
                user = await client.get_users(user_id)
                user_first_name = user.first_name
            except RPCError:
                await message.reply_text("I couldn't find that user.")
                return None, None
    else:
        # If no arguments provided, return info of the user who sent the command
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    
    return user_id, user_first_name


# User info command handler
@Client.on_message(filters.command("info"))
async def user_info_command(client: Client, message: Message):
    # Extract user ID and first name
    user_id, user_first_name = await extract_user(client, message)
    
    if not user_id:
        return
    
    try:
        # Get full user information
        user = await client.get_users(user_id)
        
        # Check if user is a bot
        is_bot = user.is_bot
        
        # Get user's status in the chat if in a group
        user_status = "N/A"
        if message.chat.type in ["group", "supergroup"]:
            try:
                chat_member = await client.get_chat_member(message.chat.id, user_id)
                user_status = chat_member.status.capitalize()
            except RPCError:
                user_status = "Unknown"
        
        # Format user joined date if available
        join_date = "Unknown"
        if hasattr(user, "joined_date") and user.joined_date:
            join_date = user.joined_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the info message
        info_text = (
            f"# User Information\n\n"
            f"**ID:** `{user_id}`\n"
            f"**First Name:** {user.first_name}\n"
        )
        
        # Add last name if available
        if user.last_name:
            info_text += f"**Last Name:** {user.last_name}\n"
        
        # Add username if available
        if user.username:
            info_text += f"**Username:** @{user.username}\n"
        
        # Add bot status
        info_text += f"**Bot:** {'Yes' if is_bot else 'No'}\n"
        
        # Add chat status if in a group
        if message.chat.type in ["group", "supergroup"]:
            info_text += f"**Status in Chat:** {user_status}\n"
        
        # Add DC ID if available
        if hasattr(user, "dc_id") and user.dc_id:
            info_text += f"**DC ID:** {user.dc_id}\n"
        
        # Add join date if available
        if join_date != "Unknown":
            info_text += f"**Joined Telegram:** {join_date}\n"
        
        # Add Jotaro-style comment
        if user_id == (await client.get_me()).id:
            info_text += "\nYare yare daze... That's me. Star Platinum's user."
        else:
            info_text += "\nStar Platinum has analyzed this user. Ora ora ora!"
        
        # Send the info message
        await message.reply_text(info_text)
        
    except RPCError as e:
        await message.reply_text(f"Error retrieving user info: {str(e)}")
