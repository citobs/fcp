from pymongo import MongoClient
import urllib.parse

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://kingofstudyway:mybd0724@test0.bmegc.mongodb.net/')
db = client['newfcp']
collection = db['newfcp']

def delete_url(url):
    # URL 디코딩 (만약 인코딩된 URL이 주어진다면)
    decoded_url = urllib.parse.unquote(url)

    # URL에서 쿼리 문자열 제거 (기본 URL만 남김)
    base_url = decoded_url.split('?')[0]  # `?` 전까지의 URL만 사용

    # 부분 URL을 기준으로 데이터를 삭제
    result = collection.delete_many({'url': {'$regex': base_url}})

    # 삭제 결과 확인
    if result.deleted_count > 0:
        print(f"URL '{decoded_url}' 에 해당하는 데이터가 성공적으로 삭제되었습니다.")
    else:
        print(f"URL '{decoded_url}' 을(를) 찾을 수 없습니다.")

if __name__ == "__main__":
    # 삭제할 URL 입력
    url_to_delete = input("삭제할 URL을 입력하세요: ")
    delete_url(url_to_delete)
