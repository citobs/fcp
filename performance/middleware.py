import logging

access_logger = logging.getLogger('access_log')


class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 요청의 IP 주소 및 경로를 기록
        client_ip = request.META.get('REMOTE_ADDR')
        request_path = request.path

        access_logger.info(f"Client IP: {client_ip}, Request Path: {request_path}")

        response = self.get_response(request)
        return response
