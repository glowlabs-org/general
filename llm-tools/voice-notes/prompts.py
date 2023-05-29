import os
import itertools
from typing import List

# Function to get all the permutations
def get_permutations(options: List[List[str]]) -> List[List[str]]:
    return list(itertools.product(*options))

# Function to read a .txt file
def read_txt_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read().strip()

def fill_template(template: str, **kwargs) -> str:
    # Hardcoded keys
    hardcoded_keys = ["context", "date", "author", "chunk"]

    for key, value in kwargs.items():
        if key in hardcoded_keys:
            template = template.replace(f"[{key}]", value)
        else:
            # Dynamically fill other keys with their respective values
            template = template.replace(f"[{key}]", value)

    return template.lstrip()  # Remove leading whitespace and newlines

def parse_options(text: str) -> (dict, str):
    lines = text.strip().split("\n")
    options_dict = {}
    key = None
    remaining_content = ""
    options_section = True  # a flag to mark if we are in the options section
    for line in lines:
        if line.strip() == '':
            options_section = False
        if options_section:
            if ':' in line:
                key, _ = line.split(':')
                options_dict[key.strip()] = []
            else:
                options_dict[key.strip()].append(line.strip())
        else:
            remaining_content += line + "\n"
    return options_dict, remaining_content

# Base directory
base_dir = 'data'

# Loop over all authors
for author in os.listdir(base_dir):
    author_dir = os.path.join(base_dir, author)
    
    if not os.path.isdir(author_dir):
        continue

    # Context of the author
    context_path = os.path.join(author_dir, 'context.txt')
    context = read_txt_file(context_path)

    # Path to chunks
    chunks_dir = os.path.join(author_dir, 'chunks')
    
    # Loop over all chunks for each author
    for chunk in os.listdir(chunks_dir):
        chunk_dir = os.path.join(chunks_dir, chunk)
        
        # Extract date from the chunk name
        date = chunk.split('-')[0]

        # Loop over all chunk files in the chunk directory
        for chunk_file in os.listdir(chunk_dir):
            chunk_path = os.path.join(chunk_dir, chunk_file)
            
            if not os.path.isfile(chunk_path):
                continue

            # Extract chunk content
            with open(chunk_path, 'r') as f:
                chunk_content = f.read()

            # Loop over all templates
            templates_dir = 'digest templates'
            for template_file in os.listdir(templates_dir):
                template_path = os.path.join(templates_dir, template_file)

                # Read the template
                template = read_txt_file(template_path)

                # Extract the options for 'parties'
                options_dict, remaining_content = parse_options(template)
                
                template = remaining_content  # Replace the template with the remaining_content

                # Create a list of lists for each category in the options dictionary
                options = [value for key, value in options_dict.items()]

                # Get all permutations of the options
                all_permutations = get_permutations(options)

                # Create a prompt for each permutation
                for i, option_perm in enumerate(all_permutations):
                    # Fill the template with the respective values from the permutation
                    filling_args = {'context': context, 'date': date, 'author': author, 'chunk': chunk_content}

                    # Update the filling_args dictionary with the option_perm converted to a list first
                    filling_args.update({key: value for key, value in zip(options_dict.keys(), list(option_perm))})

                    # Fill the template
                    filled_template = fill_template(template, **filling_args)

                    # Save the filled template to a .txt file
                    output_dir = os.path.join(author_dir, 'digest prompts', chunk, chunk_file.split('.')[0])
                    os.makedirs(output_dir, exist_ok=True)

                    output_path = os.path.join(output_dir, f"{chunk}_{template_file.split('.')[0]}_{i}.txt")
                    with open(output_path, 'w') as output_file:
                        output_file.write(filled_template)
print('All prompts have been successfully created.')
