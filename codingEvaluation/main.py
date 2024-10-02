import os

from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter


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


def run():
    docs_load()
    text_split()

if __name__ == '__main__':
    run()

