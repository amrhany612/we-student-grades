from django.db import models

# Create your models here.
class Student(models.Model):
    national_no = models.CharField(max_length=20, unique=True)  # National ID (رقم القومي)
    name = models.CharField(max_length=200)  # Student Name (اسم الطالب)
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=200)  # Subject Name
    max_score = models.IntegerField()  # Maximum score for this subject

    def __str__(self):
        return self.name

class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.FloatField()  # The score the student achieved in this subject

    def __str__(self):
        return f'{self.student.name} - {self.subject.name}: {self.score}'