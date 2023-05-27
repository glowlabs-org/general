#!/bin/bash

input_folder="audio-files"
output_folder="transcriptions"

# Create output folder if it doesn't exist
mkdir -p "$output_folder"

# Iterate through files in the input folder
for file in "$input_folder"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        extension="${filename##*.}"
        filename="${filename%.*}"

        output_file="$output_folder/$filename.tsv"

        # Run the command with the current file
        whisper "$file" --model large-v2 --output_format tsv --output_dir "$output_folder"

        echo "Transcription saved to: $output_file"
    fi
done

