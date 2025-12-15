from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    register, PlayerProfileViewSet, BuildingTypeViewSet,
    BuildingViewSet, PartyViewSet, WeaponTypeViewSet,
    TowerViewSet, WaveViewSet, EnemyViewSet,
    WorkerTypeViewSet, WorkerViewSet,
    MaterialTypeViewSet, PlayerMaterialViewSet,
    TechnologyTypeViewSet, PlayerTechnologyViewSet,
    CraftingRecipeViewSet, PlayerItemViewSet,
    TradeOfferViewSet, TerritorialExpansionViewSet, GameTickViewSet
)
from .auth_views import google_login, google_oauth_config

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
router.register(r'material-types', MaterialTypeViewSet)
router.register(r'materials', PlayerMaterialViewSet, basename='material')
router.register(r'technology-types', TechnologyTypeViewSet)
router.register(r'technologies', PlayerTechnologyViewSet, basename='technology')
router.register(r'recipes', CraftingRecipeViewSet)
router.register(r'items', PlayerItemViewSet, basename='item')
router.register(r'trades', TradeOfferViewSet, basename='trade')
router.register(r'expansions', TerritorialExpansionViewSet, basename='expansion')
router.register(r'ticks', GameTickViewSet, basename='tick')

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Google OAuth
    path('google/login/', google_login, name='google_login'),
    path('google/config/', google_oauth_config, name='google_config'),
    path('', include(router.urls)),
]
