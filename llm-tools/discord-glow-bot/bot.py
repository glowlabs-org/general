import discord
import logging
import json
import os

intents = discord.Intents.default()
intents.messages = True
intents.guild_messages = True
intents.message_content = True

# Configure root logger to ignore all messages
logging.basicConfig(level=logging.CRITICAL)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        # check if the message comes from a DM
        if isinstance(message.channel, discord.DMChannel):
            await self.handle_dm(message)
        else:
            await self.handle_server_message(message)

        if message.author != self.user and message.content == 'ping':
            await message.channel.send('pong')

    async def handle_dm(self, message):
        """
        Handles direct messages sent to the bot.

        This function logs the messages in a file named with the DM's channel ID.
        """
        log_dict = self.create_log_dict(message, True)
        file_path = os.path.join('logs', f'dm_{message.channel.id}.log')

        with open(file_path, 'a') as file:
            file.write(json.dumps(log_dict) + "\n")

    async def handle_server_message(self, message):
        """
        Handles messages in servers.

        This function creates a separate directory for each server, named with the server's name and ID.
        Inside each server's directory, it logs the messages in a file named with the channel's name.
        """
        log_dict = self.create_log_dict(message, False)
        server_path = os.path.join('logs', f'{message.guild.name}_{message.guild.id}')
        if not os.path.exists(server_path):
            os.makedirs(server_path)
        file_path = os.path.join(server_path, f'{message.channel.name}.log')

        with open(file_path, 'a') as file:
            file.write(json.dumps(log_dict) + "\n")

    @staticmethod
    def create_log_dict(message, is_dm):
        """
        Creates a dictionary for logging.

        This function separates the timestamp into two fields: 'timestamp' (unix time) and 'microseconds'.
        """
        log_dict = {
            'IsDM': is_dm,
            'author': f'{message.author.name}#{message.author.discriminator}',
            'content': message.content,
            'timestamp': int(message.created_at.timestamp()),
            'microseconds': message.created_at.microsecond,
        }
        return log_dict


# read the token from the 'token' file
with open('token', 'r') as file:
    token = file.read().strip()

client = MyClient(intents=intents)
client.run(token)
