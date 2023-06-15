import datetime
import os
import json
import collections

# Specify the directory where your chat logs are
directory = 'conversations'

def convert_timestamp(message):
    timestamp, content = message.split('] ', 1)
    timestamp = int(timestamp[1:])
    dt = datetime.datetime.fromtimestamp(timestamp)
    formatted_timestamp = dt.strftime('%Y/%m/%d %H:%M:%S')
    return f'[{formatted_timestamp}] {content}'

# Function to split the chat log into chunks
def split_log(conversation, max_len, min_overlap, max_overlap):
    chunks = []

    current_chunk = []
    current_word_count = 0

    overlap_buffer = []
    overlap_word_count = 0

    for message in conversation:
        formatted_message = convert_timestamp(message)
        message_word_count = len(message.split())

        if current_word_count + message_word_count > max_len and overlap_word_count >= min_overlap:
            chunks.append(current_chunk.copy())
            current_chunk = overlap_buffer.copy()
            current_word_count = overlap_word_count

        current_chunk.append(formatted_message)
        current_word_count += message_word_count

        if overlap_word_count + message_word_count <= max_overlap:
            overlap_buffer.append(formatted_message)
            overlap_word_count += message_word_count
        else:
            while overlap_buffer and overlap_word_count + message_word_count > max_overlap:
                removed_message = overlap_buffer.pop(0)
                overlap_word_count -= len(removed_message.split())
            overlap_buffer.append(formatted_message)
            overlap_word_count += message_word_count

    chunks.append(current_chunk)

    return chunks

# Iterate over all the json files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        with open(os.path.join(directory, filename), 'r') as f:
            data = json.load(f)

        # Split the log into chunks
        chunks = split_log(data['conversation'], 800, 250, 400)

        # Create a new directory for the chunks
        new_dir = os.path.join(directory, filename.rstrip('.json'))
        os.makedirs(new_dir, exist_ok=True)

        # Write the chunks to new json files
        for i, chunk in enumerate(chunks, start=1):
            chunk_data = {'content-type': 'conversation-v1', 'conversation': chunk}
            with open(os.path.join(new_dir, f'chunk_{i}.json'), 'w') as f:
                json.dump(chunk_data, f, indent=4)

