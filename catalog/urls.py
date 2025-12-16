from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WearViewSet

router = DefaultRouter()
router.register(r'wears', WearViewSet, basename='wears')

urlpatterns = [ path('', include(router.urls)), ]
