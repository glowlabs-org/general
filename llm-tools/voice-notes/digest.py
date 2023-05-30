import os
import aiohttp
import asyncio
import json

HOSTS = ['localhost:5000', 'localhost:5005']
URIS = [f'http://{host}/api/v1/generate' for host in HOSTS]

settings = {
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

async def run(uri, prompt_file_path, response_file_path):
    async with aiohttp.ClientSession() as session:
        with open(prompt_file_path, 'r') as f:
            prompt = f.read()

        request = {'prompt': prompt}
        request.update(settings)

        async with session.post(uri, json=request) as response:
            if response.status == 200:
                result = await response.json()
                text = result['results'][0]['text']
                result_str = prompt + text

                with open(response_file_path, 'w') as f:
                    f.write(result_str)
            else:
                print(await response.text())

def generate_file_list():
    file_list = []
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
                                response_file_path = os.path.join(chunk_responses_path, prompt_file)

                                # Check if the response file already exists, if yes skip this iteration
                                if os.path.exists(response_file_path):
                                    continue

                                file_list.append((prompt_file_path, response_file_path))

    return file_list

async def process_file_list():
    file_list = generate_file_list()
    task_queue = asyncio.Queue()

    for item in file_list:
        await task_queue.put(item)

    async def worker(uri):
        while not task_queue.empty():
            prompt_file_path, response_file_path = await task_queue.get()
            await run(uri, prompt_file_path, response_file_path)
            task_queue.task_done()

    tasks = []
    for uri in URIS:
        task = asyncio.create_task(worker(uri))
        tasks.append(task)

    await task_queue.join()
    for task in tasks:
        task.cancel()

if __name__ == '__main__':
    asyncio.run(process_file_list())
