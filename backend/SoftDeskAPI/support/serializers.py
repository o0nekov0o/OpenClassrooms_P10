from rest_framework import serializers
from .models import User, Project, Contributor, Issue, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = []


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = []


class ContributorViewset(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        exclude = []


class IssueViewset(serializers.ModelSerializer):
    class Meta:
        model = Issue
        exclude = []


class CommentViewset(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = []
