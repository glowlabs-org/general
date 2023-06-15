import os

folder = 'conversations'
total_words = 0

for filename in os.listdir(folder):
    with open(os.path.join(folder, filename), 'r') as f:
        content = f.read()
        words = content.split()
        total_words += len(content)

print(f"Total words in all files in '{folder}': {total_words}")
