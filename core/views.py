from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

# Authentication Views
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            role = user.profile.role
            if role == 'instructor':
                return redirect('instructor_dashboard')
            else:
                return redirect('student_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard Views
@login_required
def student_dashboard(request):
    return render(request, 'core/student_dashboard.html')

@login_required
def instructor_dashboard(request):
    return render(request, 'core/instructor_dashboard.html')

# Instructor Views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Lesson
from .forms import CourseForm, LessonForm
from django import forms

@login_required
def instructor_dashboard(request):
    if request.user.profile.role != 'instructor':
        return redirect('home')
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'core/instructor/dashboard.html', {'courses': courses})

@login_required
def create_course(request):
    if request.user.profile.role != 'instructor':
        return redirect('home')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    return render(request, 'core/instructor/course_form.html', {'form': form})

@login_required
def update_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    form = CourseForm(request.POST or None, instance=course)
    if form.is_valid():
        form.save()
        return redirect('instructor_dashboard')
    return render(request, 'core/instructor/course_form.html', {'form': form})

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    course.delete()
    return redirect('instructor_dashboard')

@login_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lessons = Lesson.objects.filter(course=course)
    return render(request, 'core/instructor/lesson_list.html', {'course': course, 'lessons': lessons})

# File Upload Functionality Added
import os
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Course, Lesson
from .forms import LessonForm
from .appwrite_client import storage
from appwrite.input_file import InputFile

@login_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course

            if request.FILES.get('file'):
                upload_file = request.FILES['file']

                # Save to a temporary file
                with tempfile.NamedTemporaryFile(delete=False) as temp:
                    for chunk in upload_file.chunks():
                        temp.write(chunk)
                    temp_path = temp.name

                try:
                    # Upload to Appwrite using path
                    appwrite_file = storage.create_file(
                        bucket_id="684345b50008bfe7742b",
                        file_id="unique()",
                        file=InputFile.from_path(temp_path),
                    )
                    lesson.file_id = appwrite_file['$id']
                finally:
                    os.remove(temp_path)  # Clean up temp file

            lesson.save()
            return redirect('manage_lessons', course_id=course.id)

    else:
        form = LessonForm(initial={'course': course})
        form.fields['course'].widget = forms.HiddenInput()

    return render(request, 'core/instructor/lesson_form.html', {
        'form': form,
        'course': course
    })



@login_required
def update_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    form = LessonForm(request.POST or None, instance=lesson)
    if form.is_valid():
        form.save()
        return redirect('manage_lessons', course_id=lesson.course.id)
    return render(request, 'core/instructor/lesson_form.html', {'form': form, 'course': lesson.course})

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    course_id = lesson.course.id
    lesson.delete()
    return redirect('manage_lessons', course_id=course_id)
