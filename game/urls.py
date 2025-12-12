from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    register, PlayerProfileViewSet, BuildingTypeViewSet,
    BuildingViewSet, PartyViewSet, WeaponTypeViewSet,
    TowerViewSet, WaveViewSet, EnemyViewSet,
    WorkerTypeViewSet, WorkerViewSet
)

router = DefaultRouter()
router.register(r'profile', PlayerProfileViewSet, basename='profile')
router.register(r'building-types', BuildingTypeViewSet)
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'parties', PartyViewSet, basename='party')
router.register(r'weapon-types', WeaponTypeViewSet)
router.register(r'towers', TowerViewSet, basename='tower')
router.register(r'waves', WaveViewSet, basename='wave')
router.register(r'enemies', EnemyViewSet, basename='enemy')
router.register(r'worker-types', WorkerTypeViewSet)
router.register(r'workers', WorkerViewSet, basename='worker')

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
