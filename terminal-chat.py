import sys

import conversation
import asyncio
import traceback
import os

async def run():
    choice = input("\ngpt or gemini: ")
    if choice == 'gpt':
        asst_id = os.environ["ASSISTANT_ID"]
        user_proxy = conversation.start_conversation('gpt', assistant_id=asst_id)
    elif choice == 'gemini':
        user_proxy = conversation.start_conversation('gemini')
    else:
        raise ValueError(f"Invalid choice: {choice}")

    while (True):
        user_input = input("\nUser: ")
        if (user_input.lower() == "exit"):
            break
        user_proxy.send_user_message(user_input, use_streamming=True)

        response = await user_proxy.get_assistant_message()
        if isinstance(response, str):
            print("Assistant: ", end="")
            print(response)
        else:
            sys.stdout.write("Assistant: ")
            for msg in response:
                sys.stdout.write(msg)

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except Exception as e:
        print(traceback.format_exc())