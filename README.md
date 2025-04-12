# JotaroBot - Telegram Group Management Bot

A Telegram group management bot with JoJo's Bizarre Adventure theme featuring the personality of Jotaro Kujo.

![Jotaro Kujo](https://i.imgur.com/placeholder.jpg)

## Features

### Admin Commands
- Ban/unban users
- Temporary bans
- Mute/unmute users
- Temporary mutes
- Promote/demote admins
- Message purging
- Blacklist words

### Utility Commands
- Save and retrieve notes
- Custom filters (auto-replies)
- Welcome and goodbye messages
- User information

### General Commands
- Help menu
- Bot stats
- Ping

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- MongoDB
- Telegram Bot Token from @BotFather
- API ID and API Hash from my.telegram.org

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jotaro-bot.git
cd jotaro-bot
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
MONGO_URI=your_mongodb_connection_string
OWNER_ID=your_telegram_user_id
SUDO_USERS=comma_separated_list_of_user_ids
```

4. Start the bot:
```bash
python main.py
```

## Usage

1. Add the bot to your group
2. Make the bot an admin with appropriate permissions
3. Use `/help` to see available commands

## Admin Commands

### Ban Commands
- `/ban <user> [reason]` - Ban a user
- `/unban <user> [reason]` - Unban a user
- `/tban <user> <time> [reason]` - Temporarily ban a user

### Mute Commands
- `/mute <user> [reason]` - Mute a user
- `/unmute <user> [reason]` - Unmute a user
- `/tmute <user> <time> [reason]` - Temporarily mute a user

### Admin Management
- `/promote <user>` - Promote a user to admin
- `/demote <user>` - Demote an admin to regular user

### Message Management
- `/purge` - Reply to a message to purge all messages from that point
- `/del` - Reply to a message to delete it

## Utility Commands

### Notes
- `/save <notename> <content>` - Save a note
- `/get <notename>` - Retrieve a note
- `/notes` - List all notes in the chat
- `/clear <notename>` - Delete a note

### Filters
- `/filter <keyword> <content>` - Add a filter that responds to a keyword
- `/stop <keyword>` - Remove a filter
- `/filters` - List all filters in the chat

### Blacklist
- `/blacklist <word1> [word2...]` - Add words to the blacklist
- `/unblacklist <word1> [word2...]` - Remove words from the blacklist
- `/blacklists` - List all blacklisted words

## Time Format for Temporary Bans/Mutes
- `s` for seconds (e.g., `30s`)
- `m` for minutes (e.g., `5m`)
- `h` for hours (e.g., `1h`)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Pyrogram](https://docs.pyrogram.org/) for the Telegram client
- [JoJo's Bizarre Adventure](https://en.wikipedia.org/wiki/JoJo%27s_Bizarre_Adventure) for the theme inspiration
