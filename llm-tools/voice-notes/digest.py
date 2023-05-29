import os
import requests
import json

# The original settings for the LLM API call are retained
HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate'

def run(prompt):
    request = {
        'prompt': prompt,
        'max_new_tokens': 800,
        'do_sample': True,
        'temperature': 1.3,
        'top_p': 0.4,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'repetition_penalty': 1.18,
        'top_k': 50,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['text']
        print(result)
        return prompt + result
    else:
        print(response)

def run_prompts():
    authors_dir = os.listdir("data")

    for author in authors_dir:
        author_path = os.path.join("data", author)
        prompts_path = os.path.join(author_path, 'digest prompts')
        responses_path = os.path.join(author_path, 'digest responses')

        if os.path.isdir(prompts_path):
            transcript_dirs = os.listdir(prompts_path)
            
            for transcript in transcript_dirs:
                transcript_path = os.path.join(prompts_path, transcript)
                transcript_responses_path = os.path.join(responses_path, transcript)

                if os.path.isdir(transcript_path):
                    chunk_dirs = os.listdir(transcript_path)

                    for chunk in chunk_dirs:
                        chunk_path = os.path.join(transcript_path, chunk)
                        chunk_responses_path = os.path.join(transcript_responses_path, chunk)
                        os.makedirs(chunk_responses_path, exist_ok=True)

                        if os.path.isdir(chunk_path):
                            prompt_files = os.listdir(chunk_path)

                            for prompt_file in prompt_files:
                                prompt_file_path = os.path.join(chunk_path, prompt_file)
                                
                                with open(prompt_file_path, 'r') as f:
                                    prompt = f.read()

                                result = run(prompt)

                                response_file_path = os.path.join(chunk_responses_path, prompt_file)
                                with open(response_file_path, 'w') as f:
                                    f.write(result)

if __name__ == '__main__':
    run_prompts()
