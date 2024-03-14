from rest_framework import serializers

from medtour.applications.models import TourApplication, Application, CommentTourApplication


class PostApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class ListApplicationSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField(source="region.name")
    category = serializers.StringRelatedField(source="category.title")

    class Meta:
        model = Application
        exclude = "id",


class RetrieveApplicationSerializer(serializers.ModelSerializer):
    region = serializers.StringRelatedField(source="region.name")
    category = serializers.StringRelatedField(source="category.title")

    class Meta:
        model = Application
        fields = "__all__"


class ListTourApplicationSerializer(serializers.ModelSerializer):
    application = ListApplicationSerializer(many=False, read_only=True)

    class Meta:
        model = TourApplication
        fields = "__all__"


class UpdateTourApplicationSerializer(serializers.ModelSerializer):
    tour = serializers.ReadOnlyField()

    class Meta:
        model = TourApplication
        fields = "__all__"


class CommentTourApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentTourApplication
        fields = "__all__"


class RetrieveTourApplicationSerializer(serializers.ModelSerializer):
    application = ListApplicationSerializer(many=False, read_only=True)
    application_comments = CommentTourApplicationSerializer(many=True, read_only=True)

    class Meta:
        model = TourApplication
        fields = "__all__"
