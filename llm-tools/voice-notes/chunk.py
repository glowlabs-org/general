import os
import csv

# Set the maximum number of words allowed in a slice
MAX_WORDS_PER_SLICE = 150

def get_slices(transcript):
    slices = []
    current_slice = []
    current_word_count = 0
    current_slice_start_time = transcript[1][0]
    current_slice_end_time = transcript[1][1]

    for row in transcript[1:]:  # Skip the header
        words_in_line = row[2].split()
        if current_word_count + len(words_in_line) > MAX_WORDS_PER_SLICE:
            slices.append(current_slice)
            current_slice = [row[0] + '\t' + row[1] + '\t' + row[2]]
            current_word_count = len(words_in_line)
        else:
            current_slice.append(row[0] + '\t' + row[1] + '\t' + row[2])
            current_word_count += len(words_in_line)

    # Always add the final slice
    if current_slice:
        slices.append(current_slice)

    return slices

def create_chunks(slices):
    chunks = []
    for i in range(len(slices) - 1):
        chunk = "\n".join(slices[i] + slices[i + 1])
        chunks.append(chunk)

    # Always add the final chunk
    if len(slices) > 0:
        chunks.append("\n".join(slices[-1]))

    return chunks

def write_chunks(chunks, chunk_folder_path):
    num_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        # Skip the last chunk if there are more chunks
        if num_chunks > 1 and i == num_chunks - 1:
            continue

        with open(os.path.join(chunk_folder_path, f'chunk_{i}.tsv'), 'w') as f:
            f.write(chunk)

def process_transcripts(data_folder_path):
    for root, dirs, files in os.walk(data_folder_path):
        for dir_name in dirs:
            transcript_dir_path = os.path.join(root, dir_name, 'transcripts')
            if not os.path.isdir(transcript_dir_path):
                continue

            transcript_files = [
                f for f in os.listdir(transcript_dir_path)
                if os.path.isfile(os.path.join(transcript_dir_path, f))
            ]

            for transcript_file in transcript_files:
                transcript_path = os.path.join(transcript_dir_path, transcript_file)

                with open(transcript_path, 'r') as f:
                    reader = csv.reader(f, delimiter='\t')
                    transcript = list(reader)

                slices = get_slices(transcript)
                chunks = create_chunks(slices)

                # Create the corresponding 'chunks' folder
                chunks_folder_path = os.path.join(root, dir_name, 'chunks')
                os.makedirs(chunks_folder_path, exist_ok=True)

                chunk_folder_name = os.path.splitext(transcript_file)[0]
                chunk_folder_path = os.path.join(chunks_folder_path, chunk_folder_name)
                os.makedirs(chunk_folder_path, exist_ok=True)

                write_chunks(chunks, chunk_folder_path)

# Set path to the data folder
data_folder_path = os.path.join(os.getcwd(), 'data')

# Process all transcripts
process_transcripts(data_folder_path)
