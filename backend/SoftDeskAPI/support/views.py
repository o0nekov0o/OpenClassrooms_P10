from django.db.models import Q
from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from django.contrib.auth.hashers import make_password
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
        if request.user.is_authenticated and request.user.pk == obj.pk:
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
    queryset = User.objects.order_by('-pk').distinct()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            instance.__class__.objects.get(pk=instance.pk).delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.username == request.user:
            password = serializer.validated_data['password']
            serializer.validated_data['password'] = make_password(password)
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.validated_data
        username, password, email, age, can_be_shared, can_be_contacted = \
            new_user['username'], new_user['password'], new_user['email'], \
            new_user['age'], new_user['can_be_shared'], new_user['can_be_contacted']
        if not User.objects.filter(Q(username=username) | Q(email=email)):
            User.objects.create(username=username, password=make_password(password), email=email, age=age,
                                can_be_shared=can_be_shared, can_be_contacted=can_be_contacted)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class IsAuthorOrContributorFilter(filters.BaseFilterBackend):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def filter_queryset(self, request, queryset, view):
        # checking for confirmation of project object by searching contributor attribute
        if queryset and hasattr(queryset[0], 'contributor_set'):
            return queryset.filter(Q(author=request.user) |
                                   Q(contributor__user=request.user))
        # checking for confirmation of issue object by searching project attribute
        # not including affected_to user because the affected_to user has to be a contributor in all ways
        if queryset and hasattr(queryset[0], 'project'):
            return queryset.filter(Q(author=request.user) |
                                   Q(project__contributor__user=request.user))
        # checking for confirmation of comment object by searching issue attribute
        if queryset and hasattr(queryset[0], 'issue'):
            return queryset.filter(Q(author=request.user) |
                                   Q(issue__project__contributor__user=request.user))


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
            issue_contributor = obj.project.contributor_set.get(user=request.user, project=obj.project).user
        if obj and hasattr(obj, 'issue'):
            comment_contributor = obj.issue.project.contributor_set. \
                get(user=request.user, project=obj.issue.project).user
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
    queryset = Project.objects.order_by('-time_created').distinct()
    filter_backends = [IsAuthorOrContributorFilter]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            instance.__class__.objects.get(pk=instance.pk).delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.author == request.user:
            serializer.validated_data.pop('author')
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_project = serializer.validated_data
        admin = User.objects.get(pk=1)
        if request.user.is_authenticated:
            Project.objects.create(author=request.user, title=new_project['title'],
                                   description=new_project['description'], type=new_project['type'])
            Contributor.objects.create(user=request.user, project=Project.objects.last())
            if not request.user == admin:
                Contributor.objects.create(user=admin, project=Project.objects.last())
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing contributor instances.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.order_by('-pk').distinct()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.project.author == request.user:
            instance.__class__.objects.get(pk=instance.pk).delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        project = serializer.validated_data['project']
        if not instance.__class__.objects.filter(user=user, project=project) \
                and instance.project.author == request.user and project.author == request.user:
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        project = serializer.validated_data['project']
        if not Contributor.objects.filter(user=user, project=project) and project.author == request.user:
            Contributor.objects.create(user=user, project=project)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    """
    permission_classes = [IsSuperUser | IsAuthenticated & IsAuthorOrContributor]
    serializer_class = IssueSerializer
    queryset = Issue.objects.order_by('-time_created').distinct()
    filter_backends = [IsAuthorOrContributorFilter]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            instance.__class__.objects.get(pk=instance.pk).delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.author == request.user:
            serializer.validated_data.pop('author')
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_issue = serializer.validated_data
        project, description, affected_to, statut, priority, tag = \
            new_issue['project'], new_issue['description'], new_issue['affected_to'], \
            new_issue['status'], new_issue['priority'], new_issue['tag']
        if Contributor.objects.filter(user=request.user, project=new_issue['project']):
            Issue.objects.create(project=project, author=request.user, description=description,
                                 affected_to=affected_to, status=statut, priority=priority, tag=tag)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comment instances.
    """
    permission_classes = [IsSuperUser | IsAuthenticated & IsAuthorOrContributor]
    serializer_class = CommentSerializer
    queryset = Comment.objects.order_by('-time_created').distinct()
    filter_backends = [IsAuthorOrContributorFilter]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            instance.__class__.objects.get(pk=instance.pk).delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.author == request.user:
            serializer.validated_data.pop('author')
            self.perform_update(serializer)
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_comment = serializer.validated_data
        if Contributor.objects.filter(user=request.user, project=new_comment['issue'].project):
            Comment.objects.create(issue=new_comment['issue'], author=request.user,
                                   description=new_comment['description'])
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
