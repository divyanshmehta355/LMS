# Contants
from .appwrite_client import bucket_id

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Course, Enrollment

def home(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page')
    courses = Course.objects.all()

    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if request.user.is_authenticated:
        enrolled_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
        for c in courses: c.is_enrolled = c.id in enrolled_ids
    else:
        for c in courses: c.is_enrolled = False

    paginator = Paginator(courses, 6)
    page_obj = paginator.get_page(page_number)

    context = { 'page_obj': page_obj, 'query': query, 'user': request.user }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('core/course_list.html', context, request=request)
        return JsonResponse({ 'html': html })

    return render(request, 'core/home.html', context)


# Authentication Views
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Enrollment


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
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    return render(request, 'core/student/dashboard.html', {'enrollments': enrollments})

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

# views.py
from appwrite.input_file import InputFile
from .appwrite_client import storage  # Assuming already available

@login_required
def create_course(request):
    if request.user.profile.role != 'instructor':
        return redirect('home')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user

            # Upload thumbnail to Appwrite
            if request.FILES.get('thumbnail_file'):
                file = request.FILES['thumbnail_file']
                file_bytes = file.read()

                try:
                    uploaded_file = storage.create_file(
                        bucket_id=bucket_id,
                        file_id="unique()",
                        file=InputFile.from_bytes(file_bytes, file.name),
                        permissions=["read(\"any\")"]
                    )
                    course.thumbnail_file_id = uploaded_file['$id']
                except Exception as e:
                    print("Thumbnail upload failed:", e)

            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()

    return render(request, 'core/instructor/course_form.html', {'form': form})


from appwrite.input_file import InputFile
from .appwrite_client import storage  # Assuming your Appwrite client is set up

@login_required
def update_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save(commit=False)

            # Check if a new thumbnail file is uploaded
            if request.FILES.get('thumbnail_file'):
                file = request.FILES['thumbnail_file']
                file_bytes = file.read()

                try:
                    uploaded_file = storage.create_file(
                        bucket_id=bucket_id,
                        file_id="unique()",
                        file=InputFile.from_bytes(file_bytes, file.name),
                        permissions=["read(\"any\")"]
                    )
                    course.thumbnail_file_id = uploaded_file['$id']
                except Exception as e:
                    print("Error uploading new thumbnail:", e)

            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm(instance=course)

    return render(request, 'core/instructor/course_form.html', {'form': form, 'course': course})


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
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course
from .forms import LessonForm
from django import forms

STREAMTAPE_UPLOAD_URL = "https://streamtape-uploader.onrender.com/api/files/upload"

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
                files = {'file': (upload_file.name, upload_file.read(), upload_file.content_type)}

                try:
                    response = requests.post(STREAMTAPE_UPLOAD_URL, files=files)
                    response.raise_for_status()

                    res_data = response.json()
                    lesson.file_id = res_data.get("fileId")  # Save only the Streamtape fileId
                except requests.exceptions.RequestException as e:
                    form.add_error('file', 'Failed to upload file. Please try again.')
                    return render(request, 'core/instructor/lesson_form.html', {'form': form, 'course': course})

            lesson.save()
            return redirect('manage_lessons', course_id=course.id)
    else:
        form = LessonForm(initial={'course': course})
        form.fields['course'].widget = forms.HiddenInput()

    return render(request, 'core/instructor/lesson_form.html', {'form': form, 'course': course})

import requests
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lesson
from .forms import LessonForm

STREAMTAPE_UPLOAD_URL = "https://streamtape-uploader.onrender.com/api/files/upload"

@login_required
def update_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            lesson = form.save(commit=False)

            if request.FILES.get('file'):
                uploaded_file = request.FILES['file']
                files = {'file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}

                try:
                    response = requests.post(STREAMTAPE_UPLOAD_URL, files=files)
                    response.raise_for_status()
                    res_data = response.json()

                    lesson.file_id = res_data.get("fileId")
                except requests.exceptions.RequestException as e:
                    form.add_error('file', 'Failed to upload file to Streamtape.')
                    return render(request, 'core/instructor/lesson_form.html', {
                        'form': form,
                        'course': lesson.course
                    })

            lesson.save()
            return redirect('manage_lessons', course_id=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)
        form.fields['course'].widget = forms.HiddenInput()

    return render(request, 'core/instructor/lesson_form.html', {'form': form, 'course': lesson.course})

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    course_id = lesson.course.id
    lesson.delete()
    return redirect('manage_lessons', course_id=course_id)

# Enrollment Views
from .models import Enrollment

@login_required
def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect('student_dashboard')  # or course_detail

# Student Dashboard
from .models import Course, Lesson

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Ensure only enrolled students or instructor can view
    if request.user != course.instructor and not Enrollment.objects.filter(course=course, student=request.user).exists():
        return redirect('home')

    lessons = Lesson.objects.filter(course=course)
    return render(request, 'core/student/course_detail.html', {
        'course': course,
        'lessons': lessons
    })

@login_required
def view_course_lessons(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('id')

    if not lessons.exists():
        return render(request, 'core/student/no_lessons.html', {'course': course})

    if not lesson_id:
        # Redirect to first lesson if none is specified
        first_lesson = lessons.first()
        return redirect('lesson_player', course_id=course.id, lesson_id=first_lesson.id)

    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    return render(request, 'core/student/lesson_player.html', {
        'course': course,
        'lessons': lessons,
        'current_lesson': lesson,
    })

# Track Progress
from django.shortcuts import get_object_or_404, render
from .models import Lesson, LessonProgress, Course

def lesson_player(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lesson_set.all()
    current_lesson = get_object_or_404(lessons, id=lesson_id)

    if request.user.is_authenticated:
        watched_lessons = LessonProgress.objects.filter(user=request.user, watched=True).values_list('lesson_id', flat=True)
    else:
        watched_lessons = []

    return render(request, 'core/lesson_player.html', {
    'course': course,
    'lessons': lessons,
    'current_lesson': current_lesson,
    'watched_lessons': list(watched_lessons),
})




# Toggle Manual Views
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import LessonProgress, Lesson

@require_POST
@login_required
def toggle_lesson_watch(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    progress, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    progress.watched = not progress.watched
    progress.save()
    return JsonResponse({'watched': progress.watched})


# Validation on Registration
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache

@never_cache
def validate_username(request):
    username = request.GET.get('username', '').strip()
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

@never_cache
def validate_email(request):
    email = request.GET.get('email', '')
    return JsonResponse({'exists': User.objects.filter(email__iexact=email).exists()})
