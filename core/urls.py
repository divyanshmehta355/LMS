from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),

    # Instructor Dashboard URLs
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/course/create/', views.create_course, name='create_course'),
    path('instructor/course/<int:course_id>/edit/', views.update_course, name='update_course'),
    path('instructor/course/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    path('instructor/course/<int:course_id>/lessons/', views.manage_lessons, name='manage_lessons'),
    path('instructor/course/<int:course_id>/lesson/create/', views.create_lesson, name='create_lesson'),
    path('instructor/lesson/<int:lesson_id>/edit/', views.update_lesson, name='update_lesson'),
    path('instructor/lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),

    # Course Enrollement
    path('course/<int:course_id>/enroll/', views.enroll_in_course, name='enroll_in_course'),

    # Student Dashboard URLs
    path('course/<int:course_id>/learn/', views.view_course_lessons, name='lesson_player'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/learn/<int:lesson_id>/', views.view_course_lessons, name='lesson_player'),

    path('course/<int:course_id>/lesson/<int:lesson_id>/toggle/', views.toggle_lesson_watch, name='toggle_lesson_watch'),
    path('courses/<int:course_id>/lessons/<int:lesson_id>/toggle-watch/', views.toggle_lesson_watch, name='toggle_lesson_watch'),
]
