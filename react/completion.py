import openai
import tiktoken
from typing import List


class TokenPadding:
    """Removes tokens from start or end and provides string with max token lenght provided"""

    def __init__(self, model_name: str = "gpt-3.5-turbo-16k"):
        self.encoding = tiktoken.encoding_for_model(model_name)

    def __pad__(
        self, text: str, max_length: int, pad_direction: str = "start", **kwargs
    ):
        direction2method = {"start": self.__pad_start__, "end": self.__pad_end__}
        return direction2method[pad_direction](text, max_length, **kwargs)

    def __pad_start__(self, text: str, max_length: int, **kwargs):
        tokens = self.__encode__(text, **kwargs)
        if len(tokens) > max_length:
            tokens = tokens[-max_length:]
        text = self.__decode__(tokens)
        return text

    def __pad_end__(self, text: str, max_length: int, **kwargs):
        tokens = self.__encode__(text, **kwargs)
        if len(tokens) > max_length:
            tokens = tokens[:max_length]
        text = self.__decode__(tokens)
        return text

    def __encode__(self, text: str, **kwargs):
        return self.encoding.encode(text, **kwargs)

    def __decode__(self, tokens: List[int]):
        return self.encoding.decode(tokens)

    def __call__(
        self, text: str, max_length: int, pad_direction: str = "start", **kwargs
    ):
        return self.__pad__(text, max_length, pad_direction, **kwargs)


class StreamCompletion:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def __call__(self, message: str, system_prompt: str, model: str):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        try:
            for resp in openai.ChatCompletion.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.2,
                max_tokens=2_000,
            ):
                content = resp.get("choices")[0].get("delta", {}).get("content")
                if content is not None:
                    yield content
        except Exception as err:
            print(err)
            pass


class NormalCompletion:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def __call__(self, message: str, system_prompt: str, model: str):
        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        response = openai.ChatCompletion.create(
            model=model, messages=message, temperature=0.2
        )
        content = response.choices[0].get("message").get("content")
        return content
