import json
import asyncio
import aiohttp
from typing import List, Dict
from tqdm.auto import tqdm, trange
from aiohttp.client_exceptions import ClientConnectionError
from asyncio import TimeoutError
from time import sleep

from config.config import *

async def http_post(url: str, input_text, cnt: int = 0):
    if cnt > 2:
        return input_text
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(60)) as session:
            async with session.post(
                url,
                json={"input": input_text.get("text"), "model": OPENAI_EMBEDDING_MODEL},
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            ) as response:
                data = await response.json()
                if data.get("data", [{}])[0].get("embedding", None):
                    input_text["embedding"] = data.get("data")[0].get("embedding")
                    return input_text
                else:
                    return input_text
    except ClientConnectionError:
        await asyncio.sleep(5)
        cnt += 1
        return await http_post(url, input_text, cnt)
    except TimeoutError:
        await asyncio.sleep(5)
        cnt += 1
        return await http_post(url, input_text, cnt)
    except Exception as err:
        print(f"EXCEPTION: {str(err)}")
        await asyncio.sleep(5)
        cnt += 1
        return await http_post(url, input_text, cnt)


async def __generate_embeddings__(input_texts: List[Dict]):
    tasks = [
        asyncio.create_task(http_post(OPENAI_API_URL, input_text))
        for input_text in input_texts
    ]
    results = []
    with tqdm(total=len(tasks)) as pbar:
        for coro in asyncio.as_completed(tasks):
            result = await coro
            if "embedding" in result:
                results.append(result)
            pbar.update(1)
    return results


def generate_embeddings(input_texts: List[Dict]):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(__generate_embeddings__(input_texts))
    return results
