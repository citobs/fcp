from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 메인 페이지
    path('api/performance/', views.performance_test, name='performance_test'),  # 성능 테스트 API
    path('api/average/', views.get_average_fcp_lcp, name='get_average_fcp_lcp'),  # 평균값 API

]
