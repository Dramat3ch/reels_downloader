# Instagram Reels Downloader - Telegram Bot

Bebrasaver is a Telegram bot designed to help you easily download Instagram reels. Follow the instructions below to set up the bot and start using it.

## Prerequisites

Before you start, make sure you have the following installed:

- Python: [Download Python](https://www.python.org/downloads/)

## Getting Started

1. **Install Telebot:**
   
    ```
    pip install pyTelegramBotAPI
    ```
2. **Install InstagramLoader:**

    ```bash
    pip install instagramloader
    ```

3. **Get Telegram Bot Token:**
   
   - Open Telegram and search for the BotFather.
   - Start a chat with BotFather and use the `/newbot` command to create a new bot.
   - Follow the instructions to set a name and username for your bot.
   - Once the bot is created, BotFather will provide you with a token. Copy this token.

4. **Configure Bebrasaver:**
   
   - Navigate to the Bebrasaver project directory.
   - Open the `config.py` file.
   - Paste the Telegram bot token from BotFather into the `YOUR_TELEGRAM_BOT_TOKEN` field.
     
     ```
      TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
     ```
    
      

## Usage

Start the Bebrasaver Telegram bot.

    python my_bot.py

Open Telegram and search for your bot. Start a chat with the bot and use the available commands to download Instagram reels.

## Contributing

If you'd like to contribute to Bebrasaver, feel free to fork the repository, make your changes, and submit a pull request.

