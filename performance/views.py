from django.shortcuts import render
from django.http import JsonResponse
import time
import json
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bson import ObjectId  # MongoDB ObjectId 변환을 위해 추가
from django.views.decorators.csrf import csrf_exempt  # CSRF 무시
# 성능 측정 로직
import logging

logger = logging.getLogger('performance')

# MongoDB 설정
client = MongoClient('mongodb+srv://kingofstudyway:mybd0724@test0.bmegc.mongodb.net/')
db = client['newfcp']
collection = db['newfcp']


# 메인 페이지 렌더링
@csrf_exempt
def index(request):
    return render(request, 'performance/index.html')


# ObjectId를 문자열로 변환하는 함수
def convert_objectid_to_str(data):
    """MongoDB에서 반환된 데이터를 JSON 직렬화가 가능하도록 ObjectId를 문자열로 변환"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)  # ObjectId를 문자열로 변환
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
            elif isinstance(value, list):
                data[key] = [convert_objectid_to_str(item) for item in value]
    elif isinstance(data, list):
        data = [convert_objectid_to_str(item) for item in data]
    return data


# 성능 테스트 API
@csrf_exempt
def performance_test(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            title = data.get('title')  # 'title' 값 추출

            if not url or not title:
                logger.error("URL or title is missing in the request.")
                return JsonResponse({'error': 'URL and title are required'}, status=400)

            # 성능 측정 로직 실행
            performance_data = measure_performance(url)
            performance_data["title"] = title  # 제목 포함

            # 현재 데이터를 MongoDB에 저장
            collection.insert_one(performance_data)
            logger.debug(f"Inserted data into MongoDB for URL {url} with title {title}")

            # MongoDB에서 동일한 URL의 과거 데이터 불러오기
            past_data = list(collection.find({"url": url}).sort("timestamp", -1))
            past_data = convert_objectid_to_str(past_data)

            performance_data = convert_objectid_to_str(performance_data)
            return JsonResponse({
                "current_data": performance_data,
                "past_data": past_data
            })

        except json.JSONDecodeError:
            logger.error("JSON decoding error")
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)




logger = logging.getLogger('performance')

def measure_performance(url):
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/local/chrome/chrome"  # 배포 환경의 Chrome 실행 파일 경로
    options.add_argument('--headless')  # 헤드리스 모드
    options.add_argument('--disable-gpu')  # GPU 비활성화
    options.add_argument('--no-sandbox')  # 리눅스 환경에서 권한 문제 방지

    # 캐시 비활성화 설정
    options.add_argument('--disable-cache')
    options.add_argument('--disk-cache-size=0')
    options.add_argument('--disable-application-cache')

    # Chrome 드라이버 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 네트워크 스로틀링 설정 (다운로드/업로드 속도 및 지연 시간 지정)
    driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
        'offline': False,
        'latency': 100,  # 추가 지연 시간 (ms)
        'downloadThroughput': 750 * 1024 / 8,  # 다운로드 속도 (750 kbps)
        'uploadThroughput': 250 * 1024 / 8,  # 업로드 속도 (250 kbps)
    })

    # CPU 스로틀링 설정 (Lighthouse와 유사한 환경으로 CPU 성능 제한)
    driver.execute_cdp_cmd('Emulation.setCPUThrottlingRate', {'rate': 4})  # 4배 느리게 설정

    # 성능 측정 시작 시점 기록
    start_time = time.time()  # 성능 측정 시작 시간 기록

    # 페이지 로드
    driver.get(url)

    # 성능 지표 수집을 위한 PerformanceObserver 설정
    driver.execute_script("""
    window.largestContentfulPaint = 0;
    window.firstContentfulPaint = performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 'N/A';

    const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
            if (entry.entryType === 'largest-contentful-paint') {
                // LCP의 마지막 발생 시점을 기록
                window.largestContentfulPaint = Math.max(window.largestContentfulPaint, entry.startTime);
            }
        });
    });
    observer.observe({ type: 'largest-contentful-paint', buffered: true });

    // 페이지 로드 완료 후 7초 대기 후 관찰 종료
    window.addEventListener('load', () => {
        setTimeout(() => observer.disconnect(), 7000);
    });
    """)

    # 성능 메트릭을 자바스크립트에서 가져오기
    performance_data = driver.execute_script("""
    return {
        fcp: window.firstContentfulPaint || 'N/A',
        lcp: window.largestContentfulPaint || 'N/A',
        url: arguments[0],
        timestamp: new Date().toISOString()
    };
    """, url)

    logger.info(f"Performance data from browser: {performance_data}")  # 성능 측정 데이터 로깅

    # FCP와 LCP 값 조정 로직
    fcp = performance_data['fcp']
    lcp = performance_data['lcp']

    # FCP와 LCP 중 작은 값을 FCP로, 큰 값을 LCP로 설정
    if fcp != 'N/A' and lcp != 'N/A':
        fcp, lcp = sorted([fcp, lcp])

    # 성능 측정 종료 시점 기록
    end_time = time.time()  # 성능 측정 끝 시점 기록

    # Total Load Time 계산 (끝 시점 - 시작 시점)
    total_load_time = (end_time - start_time)  # 초 단위로 총 로딩 시간 계산

    driver.quit()

    # 성능 메트릭 반환
    return {
        "url": url,
        "fcp": round(fcp, 2) if fcp != 'N/A' else "N/A",
        "lcp": round(lcp, 2) if lcp != 'N/A' else "N/A",
        "total_load_time": round(total_load_time, 2),  # 초 단위로 계산된 Total Load Time
        "timestamp": performance_data['timestamp']
    }


# 과거 성능 데이터 및 평균값 반환 API
@csrf_exempt
def get_average_fcp_lcp(request):
    try:
        all_data = list(collection.find())
        all_data = convert_objectid_to_str(all_data)

        url_data = {}
        for data in all_data:
            url = data['url']
            title = data.get('title', 'Unknown')  # title이 없는 경우 기본값 설정

            if url not in url_data:
                url_data[url] = {
                    'title': title,  # title도 추가
                    'fcp_sum': 0,
                    'lcp_sum': 0,
                    'count': 0
                }

            if data['fcp'] != 'N/A':
                url_data[url]['fcp_sum'] += data['fcp']
            if data['lcp'] != 'N/A':
                url_data[url]['lcp_sum'] += data['lcp']
            url_data[url]['count'] += 1

        averages = {}
        for url, values in url_data.items():
            fcp_avg = values['fcp_sum'] / values['count'] if values['count'] > 0 else 'N/A'
            lcp_avg = values['lcp_sum'] / values['count'] if values['count'] > 0 else 'N/A'
            averages[url] = {
                'title': values['title'],  # title 추가
                'fcp_avg': round(fcp_avg, 2) if fcp_avg != 'N/A' else 'N/A',
                'lcp_avg': round(lcp_avg, 2) if lcp_avg != 'N/A' else 'N/A'
            }

        return JsonResponse({'averages': averages}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


