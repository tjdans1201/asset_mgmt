from django.urls import path
from .views import AssetAPI,AssetDetailAPI,AssetStockAPI

urlpatterns = [
    path("/<int:id>", AssetAPI.as_view()),
    path("/<int:id>/detail", AssetDetailAPI.as_view()),
    path("/<int:id>/detail/stock", AssetStockAPI.as_view()),
]
