import openpyxl
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *


def home(request):
    return render(request, 'home.html')

from django.db import transaction
import openpyxl

def import_student_scores(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        # Start a transaction to ensure data consistency
        with transaction.atomic():
            # Load the workbook
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            # Define subjects to create if they don't already exist
            subjects_data = [
                ("اللغة العربية", 25),
                ("اللغة الإنجليزية", 25),
                ("MATH", 25),
                ("PHYSICS", 20),
                ("تخصص نظري", 65),
                ("تخصص عملي", 65),
                ("المجموع", 225),
                ("التربية الدينية", 10),
                ("التربية الوطنية", 10)
            ]
            
            # Fetch existing subjects to avoid redundant DB hits
            existing_subjects = {subject.name: subject for subject in Subject.objects.all()}

            # Create missing subjects if they don't exist
            subjects_to_create = [
                Subject(name=subject_name, max_score=max_score)
                for subject_name, max_score in subjects_data
                if subject_name not in existing_subjects
            ]
            
            if subjects_to_create:
                Subject.objects.bulk_create(subjects_to_create)

            # After creation, update the existing subject map with newly created ones
            existing_subjects.update({subject.name: subject for subject in Subject.objects.filter(name__in=[subj[0] for subj in subjects_data])})

            students_data = []
            scores_data = []

            # Iterate through rows and prepare data
            for row in sheet.iter_rows(min_row=2, max_row=89,values_only=True):
                national_id, full_name, arabic_score, english_score, math_score, physics_score, arts_score, practical_score, total_score, religion_score, national_education_score, *rest = row
                

                # Avoid creating student repeatedly. If student exists, use it
                student, created = Student.objects.get_or_create(
                    national_no=national_id,
                    defaults={'name': full_name}
                )

                subjects_scores = [
                    ("اللغة العربية", arabic_score),
                    ("اللغة الإنجليزية", english_score),
                    ("MATH", math_score),
                    ("PHYSICS", physics_score),
                    ("تخصص نظري", arts_score),
                    ("تخصص عملي",practical_score),
                    ("المجموع", total_score),
                    ("التربية الدينية", religion_score),
                    ("التربية الوطنية", national_education_score)
                ]

                for subject_name, score in subjects_scores:
                    subject = existing_subjects.get(subject_name)
                    if subject:
                        scores_data.append(Score(student=student, subject=subject, score=score))

            if scores_data:
                Score.objects.bulk_create(scores_data)

        return render(request, 'student_excel.html', {'message': 'تم رفع الملف بنجاح'})

    return render(request, 'student_excel.html')


def student_score_view(request):
    score_data = None
    student_name = None  
    student_id = None
    student_percentage = None  

    if request.method == 'GET':
        national_id = request.GET.get('national_id', None)
        
        if national_id:
            try:
                # Find the student by their national ID
                student = Student.objects.get(national_no=national_id)
                student_name = student.name  
                student_id = student.national_no

                # Get all subjects and corresponding scores for the student
                scores = Score.objects.filter(student=student)

                # Prepare dictionary to display subject names, scores, and max scores
                total_score = 0
                max_total_score = 0
                score_data = {}

                for score in scores:
                    score_data[score.subject.name] = {
                        'score': score.score,
                        'max_score': score.subject.max_score
                    }
                    total_score += score.score  # Sum actual scores
                    max_total_score += score.subject.max_score  # Sum max scores

                # Calculate percentage
                if max_total_score > 0:
                    student_percentage = (total_score / max_total_score) * 100

            except Student.DoesNotExist:
                score_data = "Student not found with the provided National ID."
        
    return render(request, 'student_score.html', {
        'score_data': score_data,
        'student_name': student_name,
        'student_id': student_id,
        'student_percentage': student_percentage  # Send percentage to template
    })
