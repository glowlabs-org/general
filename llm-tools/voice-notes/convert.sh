#!/bin/bash

data_folder="data"

# Initialize an array to hold the file paths
declare -A file_paths

# Iterate through subdirectories in the data folder
for sub_dir in "$data_folder"/*; do
    if [ -d "$sub_dir" ]; then
        input_folder="$sub_dir/audio-files"
        output_folder="$sub_dir/transcripts"
        
        # Create output folder if it doesn't exist
        mkdir -p "$output_folder"

        # Iterate through files in the input folder
        for file in "$input_folder"/*; do
            if [ -f "$file" ]; then
                # Store the file path and its output folder
                file_paths["$file"]="$output_folder"
            fi
        done
    fi
done

# Check if there are any files to process
if [ ${#file_paths[@]} -eq 0 ]; then
    echo "No files to process. Check the directory paths and try again."
    exit 1
fi

# Run the whisper command with the file paths
#whisper "${!file_paths[@]}" --model large-v2 --output_format tsv --output_dir "/tmp/transcripts"

# After whisper processing, rename all files in the corresponding output directory based on their Create Date
for file in "${!file_paths[@]}"; do
    echo $file
    # Extract metadata using exiftool
    datetime=$(exiftool -s3 -d "%Y-%m-%d %H:%M:%S" -CreateDate "$file")
    
    # Remove the path and extension from the filename
    filename=$(basename -- "$file")
    extension="${filename##*.}"
    filename="${filename%.*}"
    
    # Create new filename
    new_filename="${datetime}-${filename}.tsv"
    
    # Define the output directory for this file
    output_folder=${file_paths["$file"]}
    
    # Rename the output file
    if [ -f "/tmp/transcripts/$filename.tsv" ]; then
        mv "/tmp/transcripts/$filename.tsv" "$output_folder/$new_filename"
    fi
done
