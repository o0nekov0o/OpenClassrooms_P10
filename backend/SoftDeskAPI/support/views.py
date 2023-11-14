from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from django.core.exceptions import MultipleObjectsReturned
from rest_framework.permissions import IsAuthenticated, BasePermission

from .models import User, Project, Contributor, Issue, Comment
from .serializers import UserSerializer, ProjectSerializer, \
    ContributorSerializer, IssueSerializer, CommentSerializer


# Create your views here.
class IsSuperUser(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return False


class IsAuthenticatedOrSignup(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            return True
        if request.user.is_authenticated and request.method == "POST":
            return False
        if not request.user.is_authenticated and request.method == "POST":
            return True
        if not request.user.is_authenticated and request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.id == obj.id:
            return True
        if not request.user.is_authenticated and not request.user == obj.username:
            return False
        return False


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    permission_classes = [IsSuperUser | IsAuthenticatedOrSignup]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class IsAuthorOrContributorFilter(filters.BaseFilterBackend):
    """
    The request is authenticated as a user, or is a read-only request.
    """
    def filter_queryset(self, request, queryset, view):
        # checking for confirmation of project object by searching contributor attribute
        if queryset and hasattr(queryset[0], 'contributor_set'):
            return queryset.filter(Q(author=request.user.id) |
                                   Q(contributor__user=request.user.id))
        # checking for confirmation of issue object by searching project attribute
        # not including affected_to user because the affected_to user has to be a contributor in all ways
        if queryset and hasattr(queryset[0], 'project'):
            return queryset.filter(Q(author=request.user.id) |
                                   Q(project__contributor__user=request.user.id))
        # checking for confirmation of comment object by searching issue attribute
        if queryset and hasattr(queryset[0], 'issue'):
            return queryset.filter(Q(author=request.user.id) |
                                   Q(issue__project__contributor__user=request.user.id))


class IsAuthorOrContributor(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """
    def has_object_permission(self, request, view, obj):
        if request.user == obj.author and request.method in ['GET', 'PUT', 'PATCH', 'DELETE', 'POST']:
            return True
        project_contributor, issue_contributor, comment_contributor = [obj, obj, obj]
        if obj and hasattr(obj, 'contributor_set'):
            project_contributor = obj.contributor_set.get(user=request.user, project=obj).user
        if obj and hasattr(obj, 'project'):
            issue_contributor = obj.project.contributor_set.get(user=request.user, project=obj).user
        if obj and hasattr(obj, 'issue'):
            comment_contributor = obj.issue.project.contributor_set.get(user=request.user, project=obj).user
        if request.user in [project_contributor, issue_contributor, comment_contributor] \
                and request.method in ['GET', 'POST']:
            return True
        if request.user in [project_contributor, issue_contributor, comment_contributor] \
                and request.method in ['PUT', 'PATCH', 'DELETE']:
            return False
        return False


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    permission_classes = [IsSuperUser | IsAuthenticated & IsAuthorOrContributor]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all().distinct()
    filter_backends = [IsAuthorOrContributorFilter]


class ContributorViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing contributor instances.
    """
    permission_classes = [IsSuperUser]
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.all().distinct()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        project = serializer.validated_data['project']
        if not instance.__class__.objects.filter(user=user, project=project):
            self.perform_update(serializer)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_409_CONFLICT)

    def create(self, request, *args, **kwargs):
        # Override create method to prevent duplicate object creation
        serializer = ContributorSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        project = serializer.validated_data['project']
        if not Contributor.objects.filter(user=user, project=project):
            Contributor.objects.create(user=user, project=project)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_409_CONFLICT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    """
    permission_classes = [IsSuperUser | IsAuthenticated & IsAuthorOrContributor]
    serializer_class = IssueSerializer
    queryset = Issue.objects.all().distinct()
    filter_backends = [IsAuthorOrContributorFilter]


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comment instances.
    """
    permission_classes = [IsSuperUser | IsAuthenticated & IsAuthorOrContributor]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().distinct()
    filter_backends = [IsAuthorOrContributorFilter]
