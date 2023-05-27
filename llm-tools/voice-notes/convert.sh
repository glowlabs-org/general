#!/bin/bash

input_folder="audio-files"
output_folder="transcriptions"

# Create output folder if it doesn't exist
mkdir -p "$output_folder"

# Initialize an array to hold the file names
file_names=()

# Iterate through files in the input folder
for file in "$input_folder"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        file_names+=("$filename")
    fi
done

# Run the command with the file names
whisper "${file_names[@]}" --model large-v2 --output_format tsv --output_dir "$output_folder"
