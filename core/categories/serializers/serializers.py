from rest_framework import serializers

from categories.models import Category


class CategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category-detail', lookup_field='id')
    class Meta:
        model = Category
        fields = '__all__'