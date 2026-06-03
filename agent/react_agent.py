from langchain.agents import create_agent
from agent.tools.agent_tools import *
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
#from langchain_core.tools import tool
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt

class ReactAgent():
    def __init__(self):
        self.agent = create_agent(
            model = chat_model,
            tools = [get_weather, get_user_location, rag_summarize, fetch_external_data],
            system_prompt = load_system_prompt(),
            middleware = [monitor_tool, log_before_model, report_prompt_switch]
        )

    def execute_stream(self, query: str):
        input_dict = {"messages": [
            {"role": "user", "content": query}
        ]}
        
        for chunk in self.agent.stream(input_dict,stream_mode="values",context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"

if __name__ == "__main__":
    react_agent = ReactAgent()
    query = "给我生成我的使用报告，我的ID为1001"
    for chunk in react_agent.execute_stream(query):
        print(chunk, end="",flush=True)
            