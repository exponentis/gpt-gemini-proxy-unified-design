import asyncio
from function_tools import local_functions


class UserProxy():
    def __init__(self, mediator):
        self.mediator = mediator
        self.user_message = None
        self.asst_message = None

    def send_user_message(self, msg, use_streamming=False):
        self.asst_message = None
        self.user_message = msg
        self.mediator.set_user_message(self.user_message, use_streamming)

    def set_asst_message(self, asst_msg):
        self.asst_message = asst_msg

    async def get_assistant_message(self):
        while True:
            if self.asst_message == None:
                await asyncio.sleep(.1)
            else:
                break

        return self.asst_message

    def execute_tools(self, tool_calls):
        try:
            for tool_call in tool_calls:
                output = local_functions.execute_function(tool_call["function_name"], tool_call["arguments"])
                tool_call.update({"output" : output})

            self.mediator.tools_executed(tool_calls)
        except:
            self.mediator.error()
            raise