import time
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from config import PING_RESPONSES

@Client.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    # Record time before processing
    start_time = time.time()
    
    # Send initial message
    initial_message = await message.reply_text("⭐ Stand testing connection...")
    
    # Calculate delay
    end_time = time.time()
    delay = round((end_time - start_time) * 1000, 2)  # Convert to ms and round to 2 decimal places
    
    # Get random Jotaro style response
    ping_response = random.choice(PING_RESPONSES)
    
    # Edit message with ping result
    await initial_message.edit_text(f"{ping_response}\n\n**Ping:** `{delay}ms`")
