import os
import shutil
from dotenv import load_dotenv

from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import tiktoken


def docs_load() -> List[str]:
    """
    문서를 읽는 함수
    """

    try:
        loader = TextLoader("input/pep8.txt", encoding="utf-8").load()

        docs = []
        for doc in loader:
            docs = doc.page_content

        return docs
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return []
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return []


def text_split(corpus):
    """
    문서를 분리하는 함수
    """

    headers_to_split_on = [  # 문서를 분할할 헤더 레벨과 해당 레벨의 이름을 정의합니다.
        (
            "#",
            "Header 1",
        ),  # 헤더 레벨 1은 '#'로 표시되며, 'Header 1'이라는 이름을 가집니다.
        (
            "##",
            "Header 2",
        ),  # 헤더 레벨 2는 '##'로 표시되며, 'Header 2'라는 이름을 가집니다.
        (
            "###",
            "Header 3",
        ),  # 헤더 레벨 3은 '###'로 표시되며, 'Header 3'이라는 이름을 가집니다.
    ]

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    chunks = splitter.split_text(corpus)

    # 토크나이저 => 2028 토큰이 가장 큰 사이즈임
    # tokenizer = tiktoken.get_encoding("o200k_base")
    # for chunk in chunks:
    #     print(len(tokenizer.encode(chunk.page_content)))

    return chunks


def pep8_docs_embedding(chunk):
    """
    문서를 임베딩하는 함수
    """

    model_name = "BAAI/bge-m3"
    model_kwargs = {'device': 'cuda'}  # gpu를 사용하기 위해 설정, cpu를 사용하려면 cuda -> cpu 변경
    encode_kwargs = {'normalize_embeddings': True}
    model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    # 벡터 저장소를 저장할 디렉토리
    pep8_save_directory = "./pep8_chroma"

    print("\n잠시만 기다려주세요.\n\n")

    # 벡터저장소가 이미 존재하는지 확인
    if os.path.exists(pep8_save_directory):
        shutil.rmtree(pep8_save_directory)
        print(f"디렉토리 {pep8_save_directory}가 삭제되었습니다.\n")

    print("코딩 스타일 가이드 PEP8 문서 벡터화를 시작합니다. ")
    pep8_db = Chroma.from_documents(chunk, model, persist_directory=pep8_save_directory).as_retriever()
    pep8_bm_db = BM25Retriever.from_documents(
        chunk
    )
    print("코딩 스타일 가이드 PEP8 문서 데이터베이스가 생성되었습니다.\n")

    return pep8_db, pep8_bm_db


def chat_llm():
    """
    코딩 역량 평가에 사용되는 거대언어모델을 생성하는 함수
    """

    load_dotenv('.env')

    # LM Studio API를 사용할 경우
    llm = ChatOpenAI(
        model_name="bartowski/gemma-2-9b-it-GGUF",
        base_url=os.getenv("LM_LOCAL_URL"),
        api_key="lm-studio",
        temperature=0,
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
    )

    # OpenAI API를 사용할 경우
    # llm = ChatOpenAI(
    #     model_name="gpt-4o-mini",
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     temperature=0,
    #     streaming=True,
    #     callbacks=[StreamingStdOutCallbackHandler()],
    # )

    return llm


def run():
    docs = docs_load()
    chunk = text_split(docs)
    pep8_db, pep8_bm_db = pep8_docs_embedding(chunk)

    llm = chat_llm()


if __name__ == '__main__':
    run()
