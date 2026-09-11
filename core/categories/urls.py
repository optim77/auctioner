from django.urls import path

from categories.views import CategoryViewSet

urlpatterns = [
    path('category/', CategoryViewSet.as_view()),
]