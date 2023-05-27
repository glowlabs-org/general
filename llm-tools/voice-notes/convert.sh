#!/bin/bash

input_folder="audio-files"
output_folder="transcrips"

# Create output folder if it doesn't exist
mkdir -p "$output_folder"

# Initialize an array to hold the file names
file_names=()

# Iterate through files in the input folder
for file in "$input_folder"/*; do
    if [ -f "$file" ]; then
        file_paths+=("$file")
    fi
done

# Run the command with the file paths
whisper "${file_paths[@]}" --model large-v2 --output_format tsv --output_dir "$output_folder"
