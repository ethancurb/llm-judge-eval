import os, copy, time, glob, pickle
import openai

class ChatGPT:
    """ChatGPT 4o-mini LLM Wrapper."""

    def __init__(self):
        openai.api_key = "API_KEY_PLACEHOLDER"

    def generate(self, messages, seed=None):
        response = openai.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=messages,
            seed=seed
        )
        return response.choices[0].message.content


def my_continue_conversation(message):
    print("You: ", end="",flush=True)
    for word in message:
        print(word, end="", flush=True)
    print("\n")

    print("GPT o3:", end="", flush=True)
    my_response = ""
    messages.append({"role": "user", "content": message})
    response = model.generate(messages)
    messages.append({"role": "assistant", "content": response})
    print(response, end="", flush=True)
    my_response+=response
    print("\n")

    return my_response

def my_print(*args, **kwargs):
    elapsed_time = time.time() - start_time
    log_message = f"[{elapsed_time:.2f}s] {' '.join(map(str, args))}"
    print(log_message, **kwargs)


if __name__ == "__main__":
    start_time = time.time()

    model = ChatGPT()
    messages = [] #chat history
    message = input("Enter your Prompt (enter 'exit' or 'quit' to stop): ")
    try:
        while message.lower() not in ['exit', 'quit']: 
            response = my_continue_conversation(message)
            print("Response: \n", response)
            message = input("Enter your next Prompt (enter 'exit' or 'quit' to stop): ")
    except Exception as ex:
        my_print("Something went wrong: ")
        my_print(ex)
    