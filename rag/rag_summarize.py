from rag.vector_store import VectorStoreService
from langchain_core.prompts import PromptTemplate
from utils.prompt_loader import load_rag_prompt
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompt()
        if self.prompt_text is None:
            raise ValueError("RAG 提示词加载失败，请检查配置文件 prompts.yaml 和对应的提示词文件是否存在")
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._build_chain()

    def _build_chain(self):
        return self.prompt_template | self.model | StrOutputParser()
    
    def retriver_docs(self, query: str)->list[Document]:
        return self.retriever.invoke(query)
    
    def summarize(self, query: str)->str:
        docs = self.retriver_docs(query)
        counter = 0
        context = ""
        for doc in docs:
            counter += 1
            context += f"文档{counter}:\n参考资料内容:{doc.page_content}| 参考资料元数据:{doc.metadata}\n"

        input_dict = {"input": query, "context": context}
        return self.chain.invoke(input_dict)

if __name__ == "__main__":
    rag_summarize_service = RagSummarizeService()
    query = "小户型适合哪些扫地机器人？"
    print(rag_summarize_service.summarize(query))