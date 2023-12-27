from .gemini_api_access import *
from vertexai.preview.generative_models import Part
import asyncio


class StreamWrapper:
    def __init__(self, stream, seed):
        self.stream = stream
        self.seed = seed
        self.is_seed_consumed = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self.is_seed_consumed:
            self.is_seed_consumed = True
            part = self.seed.candidates[0].content.parts[0]
            if hasattr(part, 'text'):
                return part.text
            else:
                return ""

        chunk = next(self.stream)
        part = chunk.candidates[0].content.parts[0]
        if hasattr(part, 'text'):
            return part.text
        else:
            return ""

class AssistantProxyGemini():
    def __init__(self, mediator):
        self.mediator = mediator
        self.chat = start_chat()
        self.use_streaming = False

    def start_processing(self, user_message, use_streamming):
        self.user_message = user_message
        self.use_streaming = use_streamming
        t = asyncio.create_task(self.process(self.user_message))
        self.mediator.started(user_message)

    def submit_tool_outputs(self, results):
        result = results[0]

        t = asyncio.create_task(
            self.process(
                Part.from_function_response(
                    name=result["function_name"],
                    response={
                        "content": result["output"],
                    }
                )
            )
        )
        self.mediator.tool_outputs_submitted(results);

    async def process(self, msg):
        try:
            response = await self.get_response(msg)
            self.process_response(response)
        except Exception as e:
            self.mediator.error()
            raise

    async def get_response(self, msg):
        print(msg)
        response = None
        async def heartbeat():
            while True:
                if (response == None):
                    self.mediator.heartbeat("running")
                await asyncio.sleep(1)
        counter = asyncio.create_task(heartbeat())

        def f():
            try:
                return self.chat.send_message(msg, stream=self.use_streaming)
            except:
                counter.cancel()
                raise

        task = asyncio.to_thread(f)
        response = await task
        return response

    def process_response(self, response):
        def skip_to_the_end():
            try:
                next(response)
            except Exception:
                pass

        chunk_1 = next(response) if self.use_streaming else response
        part = chunk_1.candidates[0].content.parts[0]
        function_call = part.function_call
        function_name = function_call.name
        if function_name != '':
            function_args = {key: value for key, value in function_call.args.items()}
            if self.use_streaming: skip_to_the_end()
            self.mediator.action_required([{"function_name" : function_name, "arguments" : function_args}])
            # workaround for gemini bug
        elif str(function_call) == 'args {\n}\n':
            if self.use_streaming: skip_to_the_end()
            self.mediator.action_required([{"function_name" : "dummy", "arguments" : {}}])
        else:
            if self.use_streaming:
                self.mediator.assistant_message_retrieved(StreamWrapper(response, chunk_1))
            else:
                part = response.candidates[0].content.parts[0]
                if hasattr(part, 'text'):
                    asst_msg = part.text
                else:
                    asst_msg = ""
                self.mediator.assistant_message_retrieved(asst_msg)
