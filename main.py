import asyncio
import logging
from pyrofork import Client, idle
from pyrofork.errors import RPCError
from config import BOT_TOKEN, API_ID, API_HASH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Pyrogram client
app = Client(
    "JotaroBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def main():
    await app.start()
    logger.info("JotaroBot is now running!")
    logger.info("Good grief... Another day of work.")
    
    # Idle to keep the bot running
    await idle()
    
    # Stop the bot when we're done
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RPCError) as e:
        logger.error(f"Error: {e}")
        logger.info("JotaroBot is shutting down...")
