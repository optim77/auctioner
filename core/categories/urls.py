from categories.views import CategoryViewSet
from django.urls import path

urlpatterns = [
    path('category/', CategoryViewSet.as_view()),
]