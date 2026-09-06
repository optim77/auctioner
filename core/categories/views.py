from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from categories.models import Category
from categories.serializers.serializers import CategorySerializer
from users.permissions.permissions_utils import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]

