import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class User(AbstractUser):
    age = models.IntegerField(validators=[MinValueValidator(15), MaxValueValidator(99)])
    can_be_contacted = models.BooleanField(default=False, blank=False, null=False)
    can_be_shared = models.BooleanField(default=False, blank=False, null=False)
    REQUIRED_FIELDS = ['age']


class Project(models.Model):
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    BACKEND = 0
    FRONTEND = 1
    IOS = 2
    ANDROID = 3
    TYPE_CHOICES = ((BACKEND, 'Back-end'),
                    (FRONTEND, 'Front-end'),
                    (IOS, 'iOS'),
                    (ANDROID, 'Android'),)
    type = models.IntegerField(choices=TYPE_CHOICES, default=BACKEND)


class Contributor(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)


class Issue(models.Model):
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="issues_author")
    description = models.TextField(max_length=2048, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    affected_to = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="issues_affected_to")
    TO_DO = 0
    IN_PROGRESS = 1
    FINISHED = 2
    STATUS_CHOICES = ((TO_DO, 'To Do'),
                      (IN_PROGRESS, 'In Progress'),
                      (FINISHED, 'Finished'),)
    status = models.IntegerField(choices=STATUS_CHOICES, default=TO_DO)
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    PRIORITY_CHOICES = ((0, 'Low'),
                        (MEDIUM, 'Medium'),
                        (HIGH, 'High'),)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=LOW)
    BUG = 0
    FEATURE = 1
    TASK = 2
    TAG_CHOICES = ((BUG, 'Bug'),
                   (FEATURE, 'Feature'),
                   (TASK, 'Task'),)
    tag = models.IntegerField(choices=TAG_CHOICES, default=BUG)


class Comment(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    issue = models.ForeignKey(to=Issue, on_delete=models.CASCADE)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    description = models.CharField(max_length=8192, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
