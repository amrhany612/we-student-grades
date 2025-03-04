import openpyxl
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *


def home(request):
    return render(request, 'home.html')

@login_required(login_url='/login/')
def import_student_scores(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if request.method == 'POST' and request.FILES['excel_file']:
            excel_file = request.FILES['excel_file']
            
            # Load the workbook
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            
            # Create subjects if they don't already exist (avoiding repeated calls to the DB)
            subjects_data = [
                ("اللغة العربية", 10),
                ("اللغة الإنجليزية", 10),
                ("MATH", 10),
                ("PHYSICS", 8),
                ("المواد الفنية النظرية", 26),
                ("المجموع", 64),
                ("التربية الدينية", 4),
                ("التربية الوطنية", 4)
            ]
            
            # Fetch existing subjects to avoid redundant DB hits
            existing_subjects = {subject.name: subject for subject in Subject.objects.all()}
            
            # Create missing subjects
            subjects_to_create = [
                Subject(name=subject_name, max_score=max_score)
                for subject_name, max_score in subjects_data
                if subject_name not in existing_subjects
            ]
            
            # Bulk create missing subjects if any
            if subjects_to_create:
                Subject.objects.bulk_create(subjects_to_create)
            
            # After creation, update the existing subject map with newly created ones
            existing_subjects.update({subject.name: subject for subject in Subject.objects.filter(name__in=[subj[0] for subj in subjects_data])})

            # Start reading data from row 2 (assuming headers are in row 1)
            students_data = []
            scores_data = []
            
            # Iterate through rows and prepare data
            for row in sheet.iter_rows(min_row=2, values_only=True):
                national_id, full_name, arabic_score, english_score, math_score, physics_score, arts_score, total_score, religion_score, national_education_score = row
                
                # Avoid creating student repeatedly. If student exists, use it
                student, created = Student.objects.get_or_create(
                    national_no=national_id,
                    defaults={'name': full_name}
                )
                
                # Prepare score data for bulk creation
                subjects_scores = [
                    ("اللغة العربية", arabic_score),
                    ("اللغة الإنجليزية", english_score),
                    ("MATH", math_score),
                    ("PHYSICS", physics_score),
                    ("المواد الفنية النظرية", arts_score),
                    ("المجموع", total_score),
                    ("التربية الدينية", religion_score),
                    ("التربية الوطنية", national_education_score)
                ]
                
                # Prepare scores data for batch insert
                for subject_name, score in subjects_scores:
                    subject = existing_subjects.get(subject_name)
                    if subject:
                        scores_data.append(Score(student=student, subject=subject, score=score))
                
                students_data.append(student)  # Add student to the list for later bulk processing
            
            # Bulk create student scores in one operation (only if there are scores to insert)
            if scores_data:
                Score.objects.bulk_create(scores_data)

            return render(request, 'student_excel.html', {'message': 'تم رفع الملف بنجاح'})

        return render(request, 'student_excel.html')



def student_score_view(request):
    score_data = None
    
    if request.method == 'GET':
        national_id = request.GET.get('national_id', None)
        print(national_id)
        if national_id:
            try:
                # Find the student by their national ID
                student = Student.objects.get(national_no=national_id)
                
                # Get all the subjects and their corresponding scores for the student
                scores = Score.objects.filter(student=student)
                
                # Prepare a dictionary to display subject names and their corresponding scores
                score_data = {
                    subject.name: score.score for score in scores for subject in [score.subject]
                }
                
            except Student.DoesNotExist:
                score_data = "Student not found with the provided National ID."
        
    return render(request, 'student_score.html', {'score_data': score_data})
