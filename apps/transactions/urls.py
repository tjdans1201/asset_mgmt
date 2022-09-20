from django.urls import path
from .views import TransactionsAPI

urlpatterns = [
    path("", TransactionsAPI.as_view()),
]
