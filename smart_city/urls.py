from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api_smart.views import AmbienteViewSet, SensorViewSet, DadoSensorViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api_smart.views import SignupView

router = routers.DefaultRouter()
router.register(r'ambientes', AmbienteViewSet, basename='ambiente')
router.register(r'sensores', SensorViewSet, basename='sensor')
router.register(r'dados', DadoSensorViewSet, basename='dadosensor')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/signup/', SignupView.as_view(), name='signup'),
]
