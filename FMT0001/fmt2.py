################################################################
#                                                              #
#                SSL-ACTX | FM0001-TG                          #
#                                                              #
#  Disclaimer:                                                 #
#  This script is intended for authorized use only.            #
#  Use this code responsibly and in accordance with all        #
#  applicable guidelines and regulations.                      #
#                                                              #
#                                                              #
#  Educational purposes only...                                #
################################################################

import os
import platform
import telebot
import zipfile
import uuid
from io import BytesIO
import json, re, time, traceback
from datetime import datetime

API_TOKEN = 'BOT_TOKEN'
ALLOWED_USERS = [USER_ID] # you tg user_id 
bot = telebot.TeleBot(API_TOKEN)

current_directory = os.getcwd()

# Logging setup
log_file = 'bot_logs.json'

# Rate limiting setup
MESSAGE_LIMIT = 5  # Number of messages allowed in RATE_INTERVAL
RATE_INTERVAL = 30  # Time interval (in seconds) for MESSAGE_LIMIT
message_times = []

def truncate_filename(filename, max_length=30):
    if len(filename) > max_length:
        return filename[:max_length-3] + '...'
    return filename

def log_message(message):
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'command': truncate_filename(message.text),  # Truncate the filename if necessary
        'response': None
    }
    return log_entry

def save_log(log_entry):
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Failed to save log entry: {e}")

def list_items(directory, item_type):
    items = [item for item in os.listdir(directory) if 
             (item_type == "files" and os.path.isfile(os.path.join(directory, item))) or 
             (item_type == "directories" and os.path.isdir(os.path.join(directory, item)))]
    return items

def search_file(directory, keyword):
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if keyword.lower() in file.lower():
                matches.append(os.path.join(root, file))
    return matches

def list_drives():
    if platform.system() == "Windows":
        from string import ascii_uppercase
        drives = [f"{letter}:/" for letter in ascii_uppercase if os.path.exists(f"{letter}:/")]
    else:
        drives = [d for d in os.listdir('/mnt') if os.path.isdir(os.path.join('/mnt', d))]
    return drives

def is_user_allowed(user_id):
    return user_id in ALLOWED_USERS

def rate_limit_exceeded():
    current_time = time.time()
    # Remove old message times that are outside the RATE_INTERVAL
    message_times[:] = [t for t in message_times if t > current_time - RATE_INTERVAL]
    return len(message_times) > MESSAGE_LIMIT

def reset_message_times():
    global message_times
    message_times = []

def retry_on_failure(func):
    def wrapper(*args, **kwargs):
        try_count = 0
        while True:
            start_time = time.time()  # Start timing
            try:
                if rate_limit_exceeded():
                    if try_count == 0:
                        # Notify user about rate limit only once per RATE_INTERVAL
                        bot.send_message(args[0].chat.id, "Rate limit exceeded. Please try again later.")
                    time.sleep(1)  # Adjust sleep time as necessary
                    try_count += 1
                    continue
                result = func(*args, **kwargs)
                end_time = time.time()  # End timing
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                # Update the log entry with the execution time
                log_entry = log_message(args[0])
                log_entry['response'] = result
                log_entry['execution_time_ms'] = execution_time
                save_log(log_entry)
                
                return result
            except Exception as e:
                error_message = f"Error occurred in {func.__name__}: {e}"
                print(error_message)
                log_entry = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'error_message': error_message,
                    'execution_time_ms': None
                }
                save_log(log_entry)
                traceback.print_exc()
                time.sleep(5)  # Wait for 5 seconds before retrying
    return wrapper
    
def send_message_in_parts(chat_id, text):
    max_message_length = 4096  # Telegram message length limit
    if len(text) <= max_message_length:
        bot.send_message(chat_id, text)
    else:
        for i in range(0, len(text), max_message_length):
            bot.send_message(chat_id, text[i:i+max_message_length])

@bot.message_handler(commands=['start', 'hl', 'help'])
@retry_on_failure
def send_welcome(message):
    if is_user_allowed(message.from_user.id):
        response = "Welcome to the File Manager Bot. Use the following commands:\n" \
                   "/lf - List files\n" \
                   "/ld - List directories\n" \
                   "/fdt - File details\n" \
                   "/sf <keyword> - Search for a file\n" \
                   "/rsf <keyword> - Regex search for a file\n" \
                   "/ldr - List drives\n" \
                   "/dl <filename_or_directory> - Download a file or zip a directory\n" \
                   "/jp <directory> - Jump to a specific directory\n" \
                   "/bk - Go back to the parent directory\n" \
                   "/lg - View logs"
    else:
        response = "You are not authorized to use this bot."
    log_entry = log_message(message)
    log_entry['response'] = response
    save_log(log_entry)
    send_message_in_parts(message.chat.id, response)

@bot.message_handler(commands=['list_files', 'lf'])
@retry_on_failure
def handle_list_files(message):
    if is_user_allowed(message.from_user.id):
        files = [truncate_filename(f) for f in list_items(current_directory, "files")]
        response = "Files in current directory:\n" + "\n".join(files) if files else "No files found."
    else:
        response = "You are not authorized to use this bot."
    send_message_in_parts(message.chat.id, response)
    return response

@bot.message_handler(commands=['list_directories', 'ld'])
@retry_on_failure
def handle_list_directories(message):
    if is_user_allowed(message.from_user.id):
        directories = list_items(current_directory, "directories")
        response = "Directories in current directory:\n" + "\n".join(directories) if directories else "No directories found."
    else:
        response = "You are not authorized to use this bot."
    log_entry = log_message(message)
    log_entry['response'] = response
    save_log(log_entry)
    send_message_in_parts(message.chat.id, response)

@bot.message_handler(commands=['search_file', 'sf'])
@retry_on_failure
def handle_search_file(message):
    if is_user_allowed(message.from_user.id):
        try:
            keyword = message.text.split(maxsplit=1)[1]
            matches = search_file(current_directory, keyword)
            response = "Search results:\n" + "\n".join(matches) if matches else "No files found."
        except IndexError:
            response = "Please provide a keyword to search."
    else:
        response = "You are not authorized to use this bot."
    log_entry = log_message(message)
    log_entry['response'] = response
    save_log(log_entry)
    send_message_in_parts(message.chat.id, response)

@bot.message_handler(commands=['list_drives', 'ldr'])
@retry_on_failure
def handle_list_drives(message):
    if is_user_allowed(message.from_user.id):
        drives = list_drives()
        response = "Available drives:\n" + "\n".join(drives) if drives else "No drives found."
    else:
        response = "You are not authorized to use this bot."
    log_entry = log_message(message)
    log_entry['response'] = response
    save_log(log_entry)
    send_message_in_parts(message.chat.id, response)

@bot.message_handler(commands=['download', 'dl'])
@retry_on_failure
def handle_download(message):
    if is_user_allowed(message.from_user.id):
        try:
            path = os.path.join(current_directory, message.text.split(maxsplit=1)[1])
            if os.path.exists(path):
                if os.path.isfile(path):
                    with open(path, 'rb') as file:
                        bot.send_document(message.chat.id, file)
                elif os.path.isdir(path):
                    bytes_io = BytesIO()
                    unique_id = uuid.uuid4()
                    zip_filename = f"{unique_id}.zip"
                    with zipfile.ZipFile(bytes_io, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for root, _, files in os.walk(path):
                            for file in files:
                                zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))
                    bytes_io.seek(0)
                    bytes_io.name = zip_filename  # Set the name attribute to control the filename
                    bot.send_document(message.chat.id, bytes_io, caption=zip_filename)
            else:
                response = "File or directory does not exist."
                send_message_in_parts(message.chat.id, response)
        except IndexError:
            send_message_in_parts(message.chat.id, "Please provide a filename or directory to download.")
    else:
        send_message_in_parts(message.chat.id, "You are not authorized to use this bot.")

# 

@bot.message_handler(commands=['jump_to', 'jp'])
@retry_on_failure
def handle_jump_to(message):
    if is_user_allowed(message.from_user.id):
        global current_directory
        try:
            directory = message.text.split(maxsplit=1)[1]
            if os.path.exists(directory) and os.path.isdir(directory):
                current_directory = directory
                response = f"Jumped to {current_directory}"
            else:
                response = "Invalid directory path."
        except IndexError:
            response = "Please provide a directory path to jump to."
    else:
        response = "You are not authorized to use this bot."
    log_entry = log_message(message)
    log_entry['response'] = response
    save_log(log_entry)
    send_message_in_parts(message.chat.id, response)

@bot.message_handler(commands=['back', 'b', 'bk'])
@retry_on_failure
def handle_back(message):
    if is_user_allowed(message.from_user.id):
        global current_directory
        try:
            parent_directory = os.path.dirname(current_directory)
            if os.path.exists(parent_directory):
                current_directory = parent_directory
                response = f"Moved back to {current_directory}"
            else:
                response = "Cannot move back further."
        except Exception as e:
            response = f"An error occurred: {e}"
    else:
        response = "You are not authorized to use this bot."
    log_entry = log_message(message)
    log_entry['response'] = response
    save_log(log_entry)
    send_message_in_parts(message.chat.id, response)

@bot.message_handler(commands=['logs', 'lg'])
@retry_on_failure
def handle_logs(message):
    if is_user_allowed(message.from_user.id):
        try:
            with open(log_file, 'r') as f:
                logs = f.readlines()
                response = "Bot logs:\n" + "\n".join(logs[-10:])  # Show last 10 entries
        except FileNotFoundError:
            response = "No logs available."
    else:
        response = "You are not authorized to use this bot."
    send_message_in_parts(message.chat.id, response)
    
def search_file_with_regex(directory, pattern):
    matches = []
    regex = re.compile(pattern)
    for root, _, files in os.walk(directory):
        for file in files:
            if regex.search(file):
                matches.append(os.path.join(root, file))
    return matches

@bot.message_handler(commands=['regex_search', 'rsf'])
@retry_on_failure
def handle_regex_search(message):
    if is_user_allowed(message.from_user.id):
        try:
            pattern = message.text.split(maxsplit=1)[1]
            matches = search_file_with_regex(current_directory, pattern)
            response = "Search results:\n" + "\n".join(matches) if matches else "No files found."
        except IndexError:
            response = "Please provide a regex pattern to search."
    else:
        response = "You are not authorized to use this bot."
    bot.send_message(message.chat.id, response)
    
@bot.message_handler(commands=['file_details', 'fdt'])
@retry_on_failure
def handle_file_details(message):
    if is_user_allowed(message.from_user.id):
        try:
            file_path = os.path.join(current_directory, message.text.split(maxsplit=1)[1])
            if os.path.exists(file_path):
                stats = os.stat(file_path)
                response = f"File: {os.path.basename(file_path)}\n" \
                           f"Size: {stats.st_size} bytes\n" \
                           f"Created: {datetime.fromtimestamp(stats.st_ctime)}\n" \
                           f"Modified: {datetime.fromtimestamp(stats.st_mtime)}"
            else:
                response = "File does not exist."
        except IndexError:
            response = "Please provide a file name."
    else:
        response = "You are not authorized to use this bot."
    bot.send_message(message.chat.id, response)

def start_bot():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"An error occurred in polling: {e}")
            traceback.print_exc()
            time.sleep(10)  # Wait for 10 seconds before restarting

if __name__ == "__main__":
    start_bot()
