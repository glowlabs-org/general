import os
import aiohttp
import asyncio
import json

# The original settings for the LLM API call are retained
HOST1 = 'localhost:5000'
HOST2 = 'localhost:5005'  # second host
URI1 = f'http://{HOST1}/api/v1/generate'
URI2 = f'http://{HOST2}/api/v1/generate'

async def run(session, uri, prompt):
    request = {
        'prompt': prompt,
        'max_new_tokens': 800,
        'do_sample': True,
        'temperature': 1.05,
        'top_p': 0.3,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'repetition_penalty': 1.18,
        'top_k': 30,
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

    async with session.post(uri, json=request) as response:
        if response.status == 200:
            data = await response.json()
            try:
                result = data['results'][0]['text']
                print(prompt + result)
                return prompt + result
            except (TypeError, KeyError):
                print("Invalid response: ", data)
                return "Invalid response"
        else:
            print("Error status: ", response.status)
            return "Error status: " + str(response.status)

async def run_prompts():
    authors_dir = os.listdir("data")

    async with aiohttp.ClientSession() as session:
        tasks = []

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
                                    response_file_path = os.path.join(chunk_responses_path, prompt_file)

                                    # Check if the response file already exists, if yes skip this iteration
                                    if os.path.exists(response_file_path):
                                        continue

                                    with open(prompt_file_path, 'r') as f:
                                        prompt = f.read()

                                    # The URI is alternated for each task
                                    uri = URI1 if len(tasks) % 2 == 0 else URI2
                                    task = asyncio.ensure_future(run(session, uri, prompt))
                                    tasks.append(task)

                                    # Gather results when they are ready
                                    if len(tasks) >= 2:
                                        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                                        for task in done:
                                            result = task.result()
                                            with open(response_file_path, 'w') as f:
                                                f.write(result)

        # If tasks are remaining, wait for them and gather results
        if tasks:
            done, _ = await asyncio.wait(tasks)
            for task in done:
                result = task.result()
                with open(response_file_path, 'w') as f:
                    f.write(result)

if __name__ == '__main__':
    asyncio.run(run_prompts())
