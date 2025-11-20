# api_client.py
import os
import time
from typing import List, Dict, Optional

import openai


class ChatGPT:
    """ChatGPT LLM wrapper using OpenAI's chat completions API."""

    def __init__(self,
                 api_key: Optional[str] = None,
                 model: str = "gpt-4.1-nano"):
        """
        Parameters
        ----------
        api_key : str, optional
            OpenAI API key. If None, reads from the OPENAI_API_KEY env var.
        model : str
            Default model name to use for all calls.
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY") or "API_KEY_PLACEHOLDER"
        openai.api_key = api_key
        self.model = model

    def generate(self,
                 messages: List[Dict[str, str]],
                 seed: Optional[int] = None) -> str:
        """
        Call the chat completion API and return the assistant's message content.
        """
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            seed=seed,
            temperature=0.0,
        )
        return response.choices[0].message.content


def my_continue_conversation(model: "ChatGPT",
                             messages: List[Dict[str, str]],
                             message: str) -> str:
    """
    Optional REPL helper, similar to what you had.
    """
    print("You: ", end="", flush=True)
    print(message)
    print("\nGPT:", end=" ", flush=True)

    messages.append({"role": "user", "content": message})
    response_text = model.generate(messages)
    messages.append({"role": "assistant", "content": response_text})

    print(response_text, flush=True)
    print()
    return response_text


def my_print(start_time: float, *args, **kwargs):
    elapsed_time = time.time() - start_time
    log_message = f"[{elapsed_time:.2f}s] {' '.join(map(str, args))}"
    print(log_message, **kwargs)


if __name__ == "__main__":
    # Simple REPL for manual testing
    start_time = time.time()
    model = ChatGPT()
    messages: List[Dict[str, str]] = []

    try:
        while True:
            message = input("Enter your prompt (or 'exit' to quit): ")
            if message.lower() in {"exit", "quit"}:
                break
            my_continue_conversation(model, messages, message)
    except Exception as ex:
        my_print(start_time, "Something went wrong:", ex)
