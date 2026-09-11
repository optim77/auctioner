from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.permissions.permissions_utils import IsAdminOrReadOnly

from categories.models import Category
from categories.serializers.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]

