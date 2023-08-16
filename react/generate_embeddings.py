import os
import re
import json
import tiktoken
from typing import Any, List, Dict, Union

from qa.embedding_request import generate_embeddings


class OpenAIEmbeddings:
    def __init__(self, model_name: str = "text-embedding-ada-002"):
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.flatten = lambda lst: [item for sublist in lst for item in sublist]

    def __call__(
        self, input_pdf_content: List[Dict], chunk_size: int = 5_000, overlap: int = 20
    ) -> Union[List[Dict], None]:
        input_texts = self.__divide_document__(input_pdf_content, chunk_size, overlap)
        results = generate_embeddings(
            self.flatten(
                list(
                    map(
                        lambda txt: [
                            {
                                "text": t,
                                "src": txt.get("src"),
                                "page_no": txt.get("page_no"),
                            }
                            for t in txt.get("page_divs")
                        ],
                        input_texts,
                    )
                )
            )
        )
        return results

    def __divide_document__(
        self, input_pdf_contents: List[Dict], chunk_size: int, overlap: int
    ):
        return list(
            map(
                lambda input_page_content: self.__divide_page__(
                    input_page_content, chunk_size, overlap
                ),
                input_pdf_contents,
            )
        )

    def __divide_page__(
        self, input_page_content: Dict, chunk_size: int, overlap: int = 20
    ):
        tokens, num_tokens = self.__tokens_from_string__(
            input_page_content.get("content")
        )
        # page_divs = []
        input_page_content["page_divs"] = []
        for ix in range(0, len(tokens), chunk_size):
            if ix > 0:
                toks = tokens[ix - overlap : ix + chunk_size]
            else:
                toks = tokens[ix : ix + chunk_size]
            txt = self.encoding.decode(toks)
            input_page_content["page_divs"].append(txt)
        return input_page_content

    def __tokens_from_string__(self, string: str):
        tokens = self.encoding.encode(string, disallowed_special=())
        return tokens, len(tokens)
