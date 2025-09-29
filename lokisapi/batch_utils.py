import asyncio
from typing import List, Callable, TypeVar
from concurrent.futures import ThreadPoolExecutor, as_completed

T = TypeVar('T')
R = TypeVar('R')


def batch_process_sync(items: List[T], process_func: Callable[[T], R],
                       max_workers: int = 5, fail_fast: bool = False) -> List[R]:
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {
            executor.submit(process_func, item): (i, item)
            for i, item in enumerate(items)
        }
        
        for future in as_completed(future_to_item):
            idx, item = future_to_item[future]
            try:
                result = future.result()
                results.append((idx, result))
            except Exception:
                if fail_fast:
                    for f in future_to_item:
                        f.cancel()
                    raise
    
    results.sort(key=lambda x: x[0])
    return [r for _, r in results]


async def batch_process_async(items: List[T], process_func: Callable,
                              max_concurrent: int = 5, fail_fast: bool = False) -> List[R]:
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []
    
    async def process_with_semaphore(idx: int, item: T):
        async with semaphore:
            result = await process_func(item)
            return (idx, result)
    
    tasks = [process_with_semaphore(i, item) for i, item in enumerate(items)]
    completed = await asyncio.gather(*tasks, return_exceptions=not fail_fast)
    
    for item in completed:
        if not isinstance(item, Exception):
            results.append(item)
    
    results.sort(key=lambda x: x[0])
    return [r for _, r in results]


def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def batch_chat_completions(client, prompts: List[str], model: str = "gpt-5", 
                           max_workers: int = 5, **kwargs) -> List[str]:
    from .models import ChatMessage, ChatRole
    
    def process_prompt(prompt: str) -> str:
        messages = [ChatMessage(ChatRole.USER, prompt)]
        response = client.chat(messages, model=model, **kwargs)
        return response.choices[0]['message']['content']
    
    return batch_process_sync(prompts, process_prompt, max_workers=max_workers)


def batch_image_generations(client, prompts: List[str], max_workers: int = 3, 
                            **kwargs) -> List[str]:
    def process_prompt(prompt: str) -> str:
        response = client.generate_image_simple(prompt, **kwargs)
        return response.data[0]['url']
    
    return batch_process_sync(prompts, process_prompt, max_workers=max_workers)


async def batch_chat_completions_async(client, prompts: List[str], model: str = "gpt-5",
                                       max_concurrent: int = 5, **kwargs) -> List[str]:
    from .models import ChatMessage, ChatRole
    
    async def process_prompt(prompt: str) -> str:
        messages = [ChatMessage(ChatRole.USER, prompt)]
        response = await client.chat(messages, model=model, **kwargs)
        return response.choices[0]['message']['content']
    
    return await batch_process_async(prompts, process_prompt, max_concurrent=max_concurrent)


async def batch_image_generations_async(client, prompts: List[str], 
                                        max_concurrent: int = 3, **kwargs) -> List[str]:
    async def process_prompt(prompt: str) -> str:
        response = await client.generate_image_simple(prompt, **kwargs)
        return response.data[0]['url']
    
    return await batch_process_async(prompts, process_prompt, max_concurrent=max_concurrent)
