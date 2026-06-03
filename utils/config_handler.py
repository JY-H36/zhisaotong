'''
yaml
key: value
'''

import yaml
from utils.path_tools import get_abs_path

def load_rag_config(config_path:str = get_abs_path("config/rag.yaml"),encoding:str = "utf-8"):
    '''加载RAG配置文件'''
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.load(f,Loader=yaml.FullLoader)
    
def load_chroma_config(config_path:str = get_abs_path("config/chroma.yaml"),encoding:str = "utf-8"):
    '''加载Chroma配置文件'''
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.load(f,Loader=yaml.FullLoader)
    
def load_prompts_config(config_path:str = get_abs_path("config/prompts.yaml"),encoding:str = "utf-8"):
    '''加载提示配置文件'''
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.load(f,Loader=yaml.FullLoader)
    
def load_agent_config(config_path:str = get_abs_path("config/agent.yaml"),encoding:str = "utf-8"):
    '''加载代理配置文件'''
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.load(f,Loader=yaml.FullLoader)
    
rag_config = load_rag_config()
chroma_config = load_chroma_config()
prompts_config = load_prompts_config()
agent_config = load_agent_config()

if __name__ == "__main__":
    print(rag_config["chat_model_name"])
    print(rag_config["embedding_model_name"])