import os,hashlib
from utils.logger_handler import logger
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

def get_file_md5_hex(file_path: str): #获取文件内容的md5
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return None
    
    if not os.path.isfile(file_path):
        logger.error(f"路径不是文件: {file_path}")
        return None
    
    md5_obj = hashlib.md5()

    chunk_size = 4096  # 4KB
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
        return md5_obj.hexdigest()

    except Exception as e:
        logger.error(f"读取文件时发生错误: {file_path}, 错误: {e}")
        return None

def listdir_with_allowed_type(path: str, allowed_types: tuple[str]): #列出目录下指定类型的文件
    files = []

    if not os.path.exists(path):
        logger.error(f"路径不存在: {path}")
        return None
    if not os.path.isdir(path):
        logger.error(f"路径不是目录: {path}")
        return None
    
    for f in os.listdir(path):
        if f.lower().endswith(allowed_types):
            files.append(os.path.join(path, f))
    return tuple(files)

def pdf_loader(filepath: str, password = None, **kwargs)->list[Document]: #加载pdf文件
    return PyPDFLoader(filepath, password=password).load()

def txt_loader(filepath: str, encoding: str = "utf-8")->list[Document]: #加载txt文件
    return TextLoader(filepath, encoding=encoding).load()
