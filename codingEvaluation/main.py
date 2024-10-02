import os

from typing import List

from langchain_community.document_loaders import TextLoader


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

def run():
    docs_load()

if __name__ == '__main__':
    run()

