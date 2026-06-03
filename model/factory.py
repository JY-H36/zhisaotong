from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import BaseChatModel,ChatTongyi
from abc import ABC,abstractmethod
from typing import Optional
from utils.config_handler import rag_config

class BaseModelFactory(ABC):
    @abstractmethod
    def generator_model(self)->Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator_model(self)->Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=rag_config["chat_model_name"])
    
class EmbeddingModelFactory(BaseModelFactory):
    def generator_model(self)->Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_config["embedding_model_name"])
    
chat_model = ChatModelFactory().generator_model()
embedding_model = EmbeddingModelFactory().generator_model()