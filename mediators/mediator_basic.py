import json
from pubsub import pub

class MediatorBasic():

    def __init__(self):
        self.state = 'new'

    def set_proxies(self, asst_proxy, user_proxy):
        self.user_proxy = user_proxy
        self.asst_proxy = asst_proxy

    def set_user_message(self, user_message, stream):
        self.state = 'ready'
        self.store_state()
        self.asst_proxy.start_processing(user_message, stream)

    def started(self, user_message):
        self.state = 'started'
        self.store_state()
        pub.sendMessage("sentMessage", evt=f"📡 Sent message: {user_message}")

    def heartbeat(self, status):
        self.state = 'running'
        self.store_state()

    def error(self):
        self.state = 'error'
        self.store_state()

    def action_required(self, calls):
        self.state = 'action_required'
        self.store_state()
        self.user_proxy.execute_tools(calls)

    def tools_executed(self, tool_results):
        self.state = 'tools_executed'
        self.store_state()
        self.asst_proxy.submit_tool_outputs(tool_results)
        for result in tool_results:
            function_name = result["function_name"]
            arguments = result["arguments"]
            output = json.dumps(result["output"])
            pub.sendMessage("executedTool", evt=f"🔧 {function_name} 🔧 : {arguments} ➡️ {output}")

    def tool_outputs_submitted(self, evt):
        self.state = 'tool_outputs_submitted'
        self.store_state()

    def assistant_message_retrieved(self, asst_message):
        self.state = 'completed'
        self.store_state()
        self.user_proxy.set_asst_message(asst_message)
        pub.sendMessage("retrievedMessage", evt="📡 Retrieved message : " + str(asst_message))

    def store_state(self):
        #print(f"**state**: {self.state}")
        pass
