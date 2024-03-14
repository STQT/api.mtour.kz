from rest_framework import serializers

from medtour.pages.models import PublicOffer


class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicOffer
        fields = "__all__"
