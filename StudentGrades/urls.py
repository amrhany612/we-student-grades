from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name='home'),
    path('import-student-scores/', views.import_student_scores, name='import_student_data'),
    path('student-scores/', views.student_score_view, name='student_scores'),

]