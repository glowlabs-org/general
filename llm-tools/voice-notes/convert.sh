#!/bin/bash

input_folder="audio-files"
output_folder="transcripts"

# Create output folder if it doesn't exist
mkdir -p "$output_folder"

# Iterate through files in the input folder
for file in "$input_folder"/*; do
    if [ -f "$file" ]; then
        # Extract metadata using exiftool
        datetime=$(exiftool -s3 -d "%Y:%m:%d %H:%M:%S" -CreateDate "$file")
        
        # Replace colons and spaces in datetime
        formatted_datetime=${datetime//:/-}
        formatted_datetime=${formatted_datetime// /-}

        # Remove the path and extension from the filename
        filename=$(basename -- "$file")
        extension="${filename##*.}"
        filename="${filename%.*}"

        # Create new filename
        new_filename="${formatted_datetime}-${filename}.${extension}"
        
        # Convert audio to transcript
        whisper "$file" --model large-v2 --output_format tsv --output_file "$output_folder/$new_filename"
    fi
done
