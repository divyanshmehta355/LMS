# Authentication Forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.filter(user=user).update(role=self.cleaned_data['role'])
        return user

# Instructor Dashboard
from django import forms
from .models import Course, Lesson

class CourseForm(forms.ModelForm):
    thumbnail_file = forms.FileField(required=False)

    class Meta:
        model = Course
        fields = ['title', 'description', 'thumbnail_file']  # Must include thumbnail_file
        widgets = {
            'thumbnail_file': forms.ClearableFileInput()
        }

class LessonForm(forms.ModelForm):
    file = forms.FileField(required=False)

    class Meta:
        model = Lesson
        fields = ['course', 'title', 'content']
