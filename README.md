# ymcaBot
YMCAbot is a bot I made in my spare time of Summer 2021 to teach myself Python.

# Set up
1. The config file
In the bot's root directory, add a file called config.json. 
```json
{
  "BOT_TOKEN": "<your_token_here>"
}
```

2. FFmpeg
Install FFmpeg to the device that will run the bot. Add it to your environment variables if running on Windows. https://ffmpeg.org/download.html

3. Dependancies
Install the dependancies that are listed in installs.txt using pip

4. Audio
This repository provides none of the sounds that the bot uses. In order to add them yourself, place MP3 files in the following folders for their related commands:
  bonk: bonk command
  ymca: YMCA command
  
5. Run the bot
Run the bot by calling python bot.py
