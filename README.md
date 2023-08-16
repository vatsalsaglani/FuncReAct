# FuncReAct

ReAct using OpenAI function calling. You can bring your own actions to it. The thought, observation, final answer, and exit functions can remain the same.

## Live Demo

[![asciicast](https://asciinema.org/a/7yBbzud9OrGV00wVzp3QA1FsJ.svg)](https://asciinema.org/a/7yBbzud9OrGV00wVzp3QA1FsJ?t=15)

## Getting started

- Clone the repo

```
git clone https://github.com/vatsalsaglani/FuncReAct.git
```

- Install the requirements.

```
pip3 install -r requirements.txt
```

- Add environment variables

```
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
OPENAI_API_URL="https://api.openai.com/v1/embeddings"
OPENAI_EMBEDDING_MODEL="text-embedding-ada-002"
OPENAI_CHAT_COMPLETION_API="https://api.openai.com/v1/completions"
OPENAI_CHAT_COMPLETION_MODEL="gpt-4"
PINECONE_API_KEY="YOUR_PINECONE_API_KEY"
PINECONE_ENV="YOUR_PINECONE_ENVIRONMENT_NAME"
```

- Execute `run.py`

```
python run.py
```

## Note

Works best with GPT-4!