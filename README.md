
# SCTG_0002

This repository contains a Telegram bot designed to manage files and directories on your local system. The bot provides functionalities such as listing files and directories, searching for files, downloading files or directories, and navigating the file system.

This one's just my one of my goofy codes or so... 

## Features

- **File and Directory Listing**: List files and directories in the current working directory.
- **File Search**: Search for files by keyword within the directory.
- **Download Files/Directories**: Download individual files or entire directories as a zip archive.
- **Directory Navigation**: Jump to specific directories or navigate back to parent directories.
- **User Access Control**: Only authorized users can interact with the bot.
- **Rate Limiting**: Prevents abuse by limiting the number of commands a user can issue within a time frame.
- **Logging**: Logs all interactions, including errors and execution times, for monitoring and debugging.

## Commands

- `/start`, `/hl`, `/help`: Display the welcome message and available commands.
- `/lf`, `/list_files`: List files in the current directory.
- `/ld`, `/list_directories`: List directories in the current directory.
- `/sf <keyword>`, `/search_file <keyword>`: Search for files containing the specified keyword.
- `/ldr`, `/list_drives`: List available drives on the system.
- `/dl <filename_or_directory>`, `/download <filename_or_directory>`: Download a file or directory.
- `/jp <directory>`, `/jump_to <directory>`: Jump to the specified directory.
- `/bk`, `/back`: Navigate back to the parent directory.
- `/lg`, `/logs`: View the log entries.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SSL-ACTX/SCTG_0002.git
   cd SCTG_0002

   ```

2. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Telegram bot:**

   - Create a bot using the [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
   - Obtain your BOT token and update the `API_TOKEN` in the script.

4. **Set up the authorized users:**

   - Add the Telegram user IDs of authorized users to the `ALLOWED_USERS` list in the script.

5. **Run the bot:**

   ```bash
   python fm2.py
   ```

## Usage

After setting up and running the bot, you can interact with it via Telegram by sending the commands listed above. The bot will respond with the appropriate information or perform the requested action.

## Security

- **User Authentication**: Only users whose IDs are included in the `ALLOWED_USERS` list can interact with the bot.
- **Rate Limiting**: Prevents command spamming by limiting the number of messages a user can send within a specified time frame.

## Contributing

Contributions are welcome! If you have ideas for new features or have found a bug, please open an issue or submit a pull request.

## Acknowledgments

- [TeleBot](https://github.com/eternnoir/pyTelegramBotAPI) - For providing the Python Telegram bot API used in this project.
