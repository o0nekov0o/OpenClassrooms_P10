from rest_framework import serializers
from .models import User, Project, Contributor, Issue, Comment

url = serializers.HyperlinkedIdentityField(view_name="campaigns:promotion-detail", read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'age', 'can_be_shared', 'can_be_contacted', 'url']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'author', 'time_created', 'title', 'description', 'type', 'url']


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'url']


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'project', 'description', 'author', 'time_created',
                  'affected_to', 'status', 'priority', 'tag', 'url']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'issue', 'author', 'description', 'time_created', 'url']
