# Contants
from .appwrite_client import project_id, bucket_id

# Authentication Model
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# Instructor Dashboard
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail_file_id = models.CharField(max_length=255, blank=True, null=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_thumbnail_url(self):
        if self.thumbnail_file_id:
            return f"https://cloud.appwrite.io/v1/storage/buckets/{bucket_id}/files/{self.thumbnail_file_id}/view?project={project_id}&width=400"
        return None
    
    def __str__(self):
        return self.title
    

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    file_id = models.CharField(max_length=255, blank=True, null=True)  # Appwrite File ID

    def __str__(self):
        return f"{self.title} ({self.course.title})"

# Student Enrollement
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

# Track Lesson Progress
from django.db import models
from django.contrib.auth.models import User

class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.student.username} watched {self.lesson.title}"
    
