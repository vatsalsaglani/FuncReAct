import pinecone

from react.completion import NormalCompletion, TokenPadding
from react.embedding_request import generate_embeddings

SYSTEM_PROMPT = "You are a helpful assistant. You have to use the provided extracted text chunks in triple backticks and answer the user query/question/search provided in single backticks. If the answer is not available in the extracted text you don't answer it."


class SearchKnowledgeBase:
    def __init__(
        self,
        pinecone_api_key: str,
        pinecone_env: str,
        pinecone_index: str,
        pinecone_namespace: str,
        complete: NormalCompletion,
        token_padding: TokenPadding,
        max_length: int = 12_000,
        pad_direction: str = "end",
        model: str = "gpt-3.5-turbo-16k",
        top_k: int = 10,
    ):
        self.complete = complete
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index = pinecone.Index(pinecone_index)
        self.namespace = pinecone_namespace
        self.model = model
        self.token_padding = token_padding
        self.max_length = max_length
        self.pad_direction = pad_direction
        self.top_k = top_k

    def __get_embeddings__(self, search_text: str) -> list:
        embeddings = generate_embeddings(
            [{"text": search_text, "src": "", "page_no": ""}]
        )
        embedding = embeddings[0]
        embedding = embedding.get("embedding")
        return embedding

    def __search__(self, search_text: str) -> str:
        embedding = self.__get_embeddings__(search_text)
        ags = {
            "vector": embedding,
            "top_k": self.top_k,
            "include_metadata": True,
        }
        if self.namespace:
            ags["namespace"] = self.namespace
        sim = self.index.query(**ags)
        sim_texts = list(
            map(lambda s: s.get("metadata").get("text"), sim.get("matches"))
        )
        return " ".join(sim_texts)

    def __answer__(self, search_text: str):
        search_results = self.__search__(search_text)

        message = f"""Search Text: `{search_text}` Search Results: ```{search_results}```
        """

        message = self.token_padding(message, self.max_length, self.pad_direction)

        answer = self.complete(message, SYSTEM_PROMPT, self.model)

        return answer

    def __call__(self, search_text: str):
        answer = self.__answer__(search_text)

        return answer
