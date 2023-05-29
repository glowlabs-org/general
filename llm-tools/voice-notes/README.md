# Voice Notes Pipeline

This folder contains an AI/LLM pipeline for processing voice notes that are
recorded. The pipeline expects that the voice notes each have a single
narrator. Voice notes from each narrator go into a folder bearing the
narrator's name. Within that folder, the raw audio is put into a folder titled
'audio-files'.

Each narrator's folder needs a file titled 'context.txt' that provides a short
description of the narrator, their role at the company, and any areas of
expertise.

You can process all of the files with the following commands:
```
./convert.sh # calls whisper to get transcripts of the audio
python3 chunk.py # breaks the transcripts into chunks that can fit in the context window
python3 prompts.py # writes a set of prompts that can be passed to an LLM
python3 digest.py # runs all of the prompts that were generated
python3 ratings.py # runs ratings a subset of prompts, 0-100%
python3 merge.py # combines the outputs and ratings into new training data
```

ratings.py is a template that can be run on prompt outputs to provide a rating
establishing how well the agent is performing when its generating outputs. We
randomly rate about 1/5th of the prompt responses. The rated prompts are
included in the training data with the full original prompt and response.

The outputs of merge.py can then be used as training data, and the LLM should
learn significantly better than if it was merely learning on the raw
transcripts.

digest.py requires an instruct tuned LLM, and uses Alpaca instruct format.
