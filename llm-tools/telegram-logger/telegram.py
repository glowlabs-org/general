import asyncio
import re
import os
import json
from time import time
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Channel, User, Chat

# Login Credentials
with open("api_id", "r") as f:
    api_id = f.read().strip()
with open("api_hash", "r") as f:
    api_hash = f.read().strip()
with open("phone_number", "r") as f:
    phone_number = f.read().strip()

# This program is intended to create a database of all of the conversation
# history from a user's telegram. It grabs a bunch of conversation objects,
# then grabs history from each conversation. It puts the conversation in a
# folder called 'conversations'. If the file for that conversation already
# exists, it tries to fetch a large number of historic messages for that
# conversation to fill out the history in the database. Then it tries to fetch
# recent messages. When it's fetching recent messages, it fetches a small
# number of messages at a time until it has fetched every recent message that
# does not appear in the database.
async def main():
    # Create a client for talking to the telegram api.
    async with TelegramClient('anon', api_id, api_hash) as client:
        # Perform authentication if required.
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            await client.sign_in(phone_number, input('Enter the code: '))
            print("Signed in successfully.")

        # Fetch a list of chat histories, called 'dialogs'.
        all_dialogs = await client.get_dialogs(limit=1500)

        # Create the 'conversations' folder, which is where we will store each
        # of our conversations, one file per conversation.
        os.makedirs('conversations', exist_ok=True)

        # Pull the messages out of each dialog.
        for dialog in all_dialogs:
            # Determine the name of the conversation. If the converstaion is
            # with a user, it'll use the name of the user. If its with a
            # channel, it'll use the name of the channel, otherwise it'll use
            # 'Unknown'.
            entity = dialog.entity
            if isinstance(entity, User):
                name = f'{entity.first_name} {entity.last_name if entity.last_name else ""}'
            elif isinstance(entity, Channel):
                name = entity.title
            elif isinstance(entity, Chat):
                name = entity.title
            else:
                print("Unknown dialog name")
                name = 'Unknown'
            print("Fetching data for: ", name)

            # Determine the filename for the conversation, and loading any
            # existing data from the file.
            filename = os.path.join('conversations', f'{name.replace("/", "_")}.json')
            existing_conversation = {"content-type": "conversation-v1", "conversation": []}
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    existing_conversation = json.load(f)
 
            # Instantiate the variables that we will be using throughout the
            # function to load new and historic messages.
            conversation = existing_conversation['conversation']
            earliest_saved_timestamp = None
            latest_saved_timestamp = None

            # Grab the earliest and latest timestamp from the conversation
            # history that we already have. We are going to assume that no
            # messages are missing between these timestamps, and therefore in
            # the future we need to check whether these messages have any gaps.
            if conversation:
                earliest_saved_timestamp = int(conversation[0].split(']')[0][1:])
                latest_saved_timestamp = int(conversation[-1].split(']')[0][1:])

            # We are going to start by fetching older messages than the
            # messages that we already have. We don't mind using a high limit
            # here, because we know that every message we fetch at this stage
            # is a message that we don't have in our database. If it takes a
            # while because of the telegram ratelimit, that's okay because it's
            # getting us useful information.
            if earliest_saved_timestamp:
                older_messages = []
                more_messages = True
                max_id = 0
                while more_messages:
                    batch_of_messages = []
                    async for message in client.iter_messages(dialog.entity, offset_date=earliest_saved_timestamp-1, limit=2000, max_id=max_id):
                        sender = await message.get_sender()
                        if sender:
                            if isinstance(sender, User):
                                sender_name = sender.first_name
                            elif isinstance(sender, Channel):
                                sender_name = sender.title
                            else:
                                print("Unknown sender")
                                sender_name = 'Unknown'
                        else:
                            print("Unknown get_sender result")
                            sender_name = 'Unknown'

                        batch_of_messages.append(f'[{int(message.date.timestamp())}] {sender_name}: {message.text}')
                        max_id = message.id

                    if batch_of_messages:
                        # Reverse the messages in this batch so that they are in chronological order
                        batch_of_messages.reverse()
                        older_messages = batch_of_messages + older_messages
                        print("Found older messages for conversation:", len(batch_of_messages))
                    else:
                        # If we didn't get any messages in the last batch, there are no more messages to fetch
                        more_messages = False

                if older_messages:
                    conversation = older_messages + conversation
                    print("Total older messages found for conversation:", len(older_messages))

            # Fetch the most recent messages. We fetch a small number of
            # messages each iteration of the loop, and then determine whether
            # its possible that more recent messages exist.
            all_new_messages = []
            earliest_new_timestamp = time()
            possible_gap = True
            while possible_gap == True:
                # If we don't have conversation history, we should only fetch
                # recent messages once.
                if not conversation:
                    possible_gap = False

                # When fetching new messages, we only grab a few at a time
                # because we may be grabbing messages that we already have, and
                # the ratelimit only gives us 30 messages per second, so
                # fetching data that we already have has a high and unnecessary
                # performance penalty.
                print("Fetching new messages...")
                new_messages = []
                async for message in client.iter_messages(dialog.entity, offset_date=earliest_new_timestamp, limit=100):
                    # Determine the name of the entity that sent the message.
                    sender = await message.get_sender()
                    if sender:
                        if isinstance(sender, User):
                            sender_name = sender.first_name
                        elif isinstance(sender, Channel):
                            sender_name = sender.title
                        elif isinstance(sender, Chat):
                            sender_name = sender.title
                        else:
                            print("Unknown sender")
                            sender_name = 'Unknown'
                    else:
                        print("Unknown result of get_sender()")
                        sender_name = 'Unknown'

                    # Add the message to the conversation, but only if the
                    # timestamp is after the latest message in the conversation.
                    if message.date.timestamp() < earliest_new_timestamp:
                        earliest_new_timestamp = message.date.timestamp()
                    if not latest_saved_timestamp or message.date.timestamp() > latest_saved_timestamp:
                        new_messages.append(f'[{int(message.date.timestamp())}] {sender_name}: {message.text}')
                    else:
                        possible_gap = False

                # Add the new messages to the front of all_new_messages, as
                # these messages are older than the messages we already
                # fetched.
                new_messages.reverse()
                all_new_messages = new_messages + all_new_messages

            # Add the new messages and ensure that they are sorted
            # chronologically. The order that we fetch messages from the
            # telegram api should preserve the chronological sorting already.
            if all_new_messages:
                conversation = conversation + all_new_messages

            # Save the new data to the file, replacing the conversation in the
            # file structure with the conversation that we've now assembled.
            existing_conversation['conversation'] = conversation
            with open(filename, 'w') as f:
                json.dump(existing_conversation, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
