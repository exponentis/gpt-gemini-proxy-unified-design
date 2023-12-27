import json
from transitions import Machine, State
from pubsub import pub

class MediatorStateMachine():

    def __init__(self):
        self._subscriptions = []
        self.initiate_state_machine()

    def initiate_state_machine(self):
        states = [
            State(name='new'),
            State(name='ready'),
            State(name='started', on_enter=self.on_started),
            State(name='requires_action'),
            State(name='tools_executed', on_enter=self.on_tools_executed),
            State(name='tool_outputs_submitted'),
            State(name='completed', on_enter=self.on_completed),
            State(name='running'),
            State(name='error')
        ]

        machine = Machine( model=self, states=states, initial='new', send_event=False)
        transition = machine.add_transition

        # the fastest way through the cycle, no actions
        transition('set_user_message', 'new', 'ready', after='_start_processing')
        transition('started', 'ready', 'started')
        transition('assistant_message_retrieved', 'started', 'completed', after='_receive_asst_message')

        # the fastest way through the cycle, with actions
        transition('action_required', 'started', 'requires_action', after='_execute_tools')
        transition('tools_executed', 'requires_action', 'tools_executed', after='_submit_tool_outputs')
        transition('tool_outputs_submitted', 'tools_executed', 'tool_outputs_submitted')
        transition('assistant_message_retrieved', 'tool_outputs_submitted', 'completed', after='_receive_asst_message')

        # action after action
        transition('action_required', 'tool_outputs_submitted', 'requires_action', after='_execute_tools')

        # accomodate for the 'running' state (i.e.'in_progress' and 'queued')
        transition('action_required', 'running', 'requires_action', after='_execute_tools')
        transition('assistant_message_retrieved', 'running', 'completed', after='_receive_asst_message')
        transition('heartbeat', 'started', 'running')
        transition('heartbeat', 'tool_outputs_submitted', 'running')
        transition('heartbeat', 'running', 'running')

        # restart
        transition('set_user_message', 'completed', 'ready', after='_start_processing')

        transition('error', '*', 'error')
        transition('set_user_message', 'error', 'ready', after='_start_processing')

        for state in states:
            state.on_enter.append(self._store_state)

        self.machine = machine

    def set_proxies(self, asst_proxy, user_proxy):
        self.user_proxy = user_proxy
        self.asst_proxy = asst_proxy

    def _start_processing(self, evt, stream=False):
        self.asst_proxy.start_processing(evt, stream)

    def _receive_asst_message(self, evt):
        self.user_proxy.set_asst_message(evt)

    def _execute_tools(self, evt):
        self.user_proxy.execute_tools(evt)

    def _submit_tool_outputs(self, evt):
        self.asst_proxy.submit_tool_outputs(evt)

    def _store_state(self, *args):
        #print(f"**state**: {self.state}")
        pass

    def on_completed(self, asst_message):
        pub.sendMessage("retrievedMessage", evt="📡 Retrieved message : " + str(asst_message))

    def on_started(self, user_message):
        pub.sendMessage("sentMessage", evt=f"📡 Sent message: {user_message}")

    def on_tools_executed(self, results):
        for result in results:
            function_name = result["function_name"]
            arguments = result["arguments"]
            output = json.dumps(result["output"])
            pub.sendMessage("executedTool", evt=f"🔧 {function_name} 🔧 : {arguments} ➡️ {output}")