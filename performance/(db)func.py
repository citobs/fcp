from pymongo import MongoClient
from bson import ObjectId  # MongoDB의 고유 ObjectId 형식을 사용하기 위해 추가

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://kingofstudyway:mybd0724@test0.bmegc.mongodb.net/')
db = client['newfcp']
collection = db['newfcp']


def create_document(data):
    """
    새 문서를 컬렉션에 삽입합니다.

    Parameters:
    - data (dict): 추가할 문서의 데이터
      예시: {
          "url": "https://example.com",
          "fcp": 1.2,
          "lcp": 2.3,
          "timestamp": "2024-10-30T12:34:56"
      }

    Returns:
    - inserted_id (ObjectId): 삽입된 문서의 ID
    """
    result = collection.insert_one(data)
    print("문서가 성공적으로 추가되었습니다.")
    return result.inserted_id


def read_documents(query={}, limit=10):
    """
    컬렉션에서 문서를 검색하여 반환합니다.

    Parameters:
    - query (dict): 검색 조건 (기본값은 빈 객체, 즉 모든 문서 검색)
      예시: {"url": "https://example.com"}
    - limit (int): 가져올 문서의 최대 개수 (기본값은 10)

    Returns:
    - documents (list): 검색된 문서의 리스트
    """
    documents = collection.find(query).limit(limit)
    return list(documents)


def update_document(document_id, updated_data):
    """
    문서를 업데이트합니다.

    Parameters:
    - document_id (str): 업데이트할 문서의 ID
      예시: "60a7b2d3b1f2b6e9b6cddf73"
    - updated_data (dict): 업데이트할 데이터
      예시: {"fcp": 1.5, "lcp": 2.8}

    Returns:
    - matched_count (int): 일치하는 문서의 수
    - modified_count (int): 수정된 문서의 수
    """
    result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": updated_data})
    print("문서가 성공적으로 업데이트되었습니다.")
    return result.matched_count, result.modified_count


def delete_document(document_id):
    """
    문서를 삭제합니다.

    Parameters:
    - document_id (str): 삭제할 문서의 ID
      예시: "60a7b2d3b1f2b6e9b6cddf73"

    Returns:
    - deleted_count (int): 삭제된 문서의 수
    """
    result = collection.delete_one({"_id": ObjectId(document_id)})
    if result.deleted_count > 0:
        print("문서가 성공적으로 삭제되었습니다.")
    else:
        print("해당 문서를 찾을 수 없습니다.")
    return result.deleted_count


def delete_by_url(url):
    """
    URL을 기준으로 문서를 삭제합니다.

    Parameters:
    - url (str): 삭제할 문서의 URL
      예시: "https://example.com"

    Returns:
    - deleted_count (int): 삭제된 문서의 수
    """
    result = collection.delete_many({"url": url})
    print(f"{result.deleted_count}개의 문서가 URL '{url}' 로 삭제되었습니다.")
    return result.deleted_count


def count_documents(query={}):
    """
    컬렉션에서 특정 조건에 맞는 문서의 개수를 반환합니다.

    Parameters:
    - query (dict): 조건을 정의하는 딕셔너리 (기본값은 모든 문서 개수)
      예시: {"url": "https://example.com"}

    Returns:
    - count (int): 문서의 개수
    """
    count = collection.count_documents(query)
    return count

# 전체 문서 개수 조회 함수
def count_all_documents():
    """
    컬렉션 내 모든 문서의 개수를 반환합니다.

    Returns:
    - count (int): 전체 문서의 개수
    """
    return collection.count_documents({})


# 특정 URL의 문서 개수 조회 함수
def count_documents_by_url(url):
    """
    특정 URL과 일치하는 문서의 개수를 반환합니다.

    Parameters:
    - url (str): 조회할 URL 값
      예시: "https://example.com"

    Returns:
    - count (int): 해당 URL과 일치하는 문서의 개수
    """
    return collection.count_documents({"url": url})


# 스크립트를 독립적으로 테스트하기 위한 블록
if __name__ == "__main__":
    rd = read_documents({"url": "https://www.amoremall.com"}, limit=10)
    print(rd)

    rdc = count_all_documents()
    print("전채개수:",rdc)

    url = "https://www.amoremall.com"
    rdcu = count_documents_by_url(url)
    print(f'"특정url":{url}',rdcu)
    # 예제 데이터 생성
    # sample_data = {
    #     "url": "https://example.com",
    #     "fcp": 1.2,
    #     "lcp": 2.3,
    #     "timestamp": "2024-10-30T12:34:56"
    # }
    # 데이터 생성
    # doc_id = create_document(sample_data)
    #
    # # 데이터 읽기
    # print("문서 검색 결과:", read_documents())
    #
    # # 데이터 업데이트
    # update_document(doc_id, {"fcp": 1.5, "lcp": 2.8})
    #
    # # 데이터 삭제
    # delete_document(doc_id)
    #
    # # URL을 기준으로 문서 삭제
    # delete_by_url("https://example.com")
    #
    # # 문서 개수 확인
    # print("전체 문서 개수:", count_documents())
