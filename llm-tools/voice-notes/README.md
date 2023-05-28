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
./chunk.py # breaks the transcripts into chunks that can fit in the context window
./prompts.py # writes a set of prompts that can be passed to an LLM
./digest.py # runs all of the prompts that were generated
./merge.py # combines the outputs into new training data
```

The outputs of merge.py can then be used as training data, and the LLM should
learn significantly better than if it was merely learning on the raw
transcripts.

digest.py requires an instruct tuned LLM, and uses Alpaca instruct format.
