from typing import Callable, Optional, Iterator, AsyncIterator, Any
import json


class StreamCallback:
    def on_start(self):
        pass
    
    def on_token(self, token: str):
        pass
    
    def on_complete(self, full_response: str):
        pass
    
    def on_error(self, error: Exception):
        pass


class PrintStreamCallback(StreamCallback):
    def on_token(self, token: str):
        print(token, end='', flush=True)
    
    def on_complete(self, full_response: str):
        print()


class BufferStreamCallback(StreamCallback):
    def __init__(self):
        self.buffer = []
        self.full_text = ""
    
    def on_token(self, token: str):
        self.buffer.append(token)
    
    def on_complete(self, full_response: str):
        self.full_text = full_response


class FileStreamCallback(StreamCallback):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = None
    
    def on_start(self):
        self.file = open(self.filepath, 'w', encoding='utf-8')
    
    def on_token(self, token: str):
        if self.file:
            self.file.write(token)
            self.file.flush()
    
    def on_complete(self, full_response: str):
        if self.file:
            self.file.close()


def stream_with_callback(stream_iterator: Iterator, callback: Optional[StreamCallback] = None):
    if callback:
        callback.on_start()
    
    full_response = ""
    
    try:
        for chunk in stream_iterator:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].get('delta', {})
                content = delta.get('content', '')
                
                if content:
                    full_response += content
                    if callback:
                        callback.on_token(content)
        
        if callback:
            callback.on_complete(full_response)
        
        return full_response
    
    except Exception as e:
        if callback:
            callback.on_error(e)
        raise


async def async_stream_with_callback(stream_iterator: AsyncIterator, callback: Optional[StreamCallback] = None):
    if callback:
        callback.on_start()
    
    full_response = ""
    
    try:
        async for chunk in stream_iterator:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].get('delta', {})
                content = delta.get('content', '')
                
                if content:
                    full_response += content
                    if callback:
                        callback.on_token(content)
        
        if callback:
            callback.on_complete(full_response)
        
        return full_response
    
    except Exception as e:
        if callback:
            callback.on_error(e)
        raise
