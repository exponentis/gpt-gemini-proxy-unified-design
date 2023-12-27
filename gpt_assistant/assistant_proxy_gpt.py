import asyncio

from .openai_access import *

from openai.types.beta import Thread
from openai.types.beta.threads import ThreadMessage, Run
import json

class AssistantProxyGpt():
    def __init__(self, mediator, asst_id):
        self.mediator = mediator
        self.asst_id = asst_id
        self.create_thread()
        self.run_id = None

    def create_thread(self):
        thread: Thread = create_thread()
        self.thread_id = thread.id
    def create_message(self, msg):
        thread_message: ThreadMessage = create_message(self.thread_id, "user", msg
                                                                     )

    def create_run(self):
        run: Run = create_run(thread_id=self.thread_id, assistant_id=self.asst_id)
        self.run_id = run.id

    def start_processing(self, user_message, use_streamming):
        self.run_id = None
        self.create_message(user_message)
        self.create_run()
        asyncio.create_task(self.process())

        self.mediator.started(user_message)

    async def process(self):
        #TODO timeout
        while (True):
            run_status = get_run(thread_id=self.thread_id, run_id=self.run_id)

            if run_status.status == 'completed':
                result =  self.retrieve_completed_message()
                self.mediator.assistant_message_retrieved(result)
                break
            elif run_status.status == 'requires_action':
                list = []
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                for tool_call in tool_calls:
                    result = {
                        "call_id" : tool_call.id,
                        "function_name" : tool_call.function.name,
                        "arguments" : json.loads(tool_call.function.arguments),
                    }
                    list.append(result)
                self.mediator.action_required(list)
            elif run_status.status in ['in_progress', 'queued']:
                self.mediator.heartbeat(run_status.status)
                await asyncio.sleep(1)
            else:
                raise Exception(f"Non-actionable status: {run_status.status}")

    def retrieve_completed_message(self):
        messages = get_thread_messages(thread_id=self.thread_id)
        response = messages.data[0].content[0].text.value
        return response

    def submit_tool_outputs(self, evt):
        tool_outputs = [{"tool_call_id": result["call_id"], "output":json.dumps(result["output"])} for result in evt]
        submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run_id,
            tool_outputs=tool_outputs
        )

        self.mediator.tool_outputs_submitted(evt);