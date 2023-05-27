#!/bin/bash

input_folder="audio-files"
output_folder="transcripts"

# Create output folder if it doesn't exist
mkdir -p "$output_folder"

# Initialize an array to hold the file paths
file_paths=()

# Iterate through files in the input folder
for file in "$input_folder"/*; do
    if [ -f "$file" ]; then
        file_paths+=("$file")
    fi
done

# Run the command with the file paths
whisper "${file_paths[@]}" --model large-v2 --output_format tsv --output_dir "$output_folder"

# After whisper processing, rename all files in the output directory based on their Create Date
for file in "${file_paths[@]}"; do
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
    new_filename="${formatted_datetime}-${filename}.tsv"
    
    # Rename the output file
    if [ -f "$output_folder/$filename.tsv" ]; then
        mv "$output_folder/$filename.tsv" "$output_folder/$new_filename"
    fi
done
