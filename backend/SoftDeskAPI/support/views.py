from rest_framework import viewsets
from .serializers import ProjectSerializer
from .models import User, Project, Contributor, Issue, Comment


# Create your views here.


class UserViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer
    queryset = User.objects.all()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()


class ContributorViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer
    queryset = Contributor.objects.all()


class IssueViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer
    queryset = Issue.objects.all()


class CommentViewset(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer
    queryset = Comment.objects.all()
