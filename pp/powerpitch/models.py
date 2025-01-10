from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import random

class Students(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    def generate_student_id():
        last_student = Students.objects.all().order_by('Student_Id').last()
        if not last_student:
            return 'CCPP001'
        
        last_id = last_student.Student_Id
        next_number = int(last_id[4:]) + 1
        return f'CCPP{next_number:03d}'

    Student_Id = models.CharField(max_length=11, primary_key=True, default=generate_student_id, editable=False)
    First_Name = models.CharField(max_length=100)
    Last_Name = models.CharField(max_length=100)
    Gmail = models.EmailField(unique=True)
    Password = models.CharField(max_length=128)  # For storing hashed password
    Gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    Branch = models.CharField(max_length=50)
    Roll_No = models.CharField(max_length=10)
    Year = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name} ({self.Student_Id})"

    def set_password(self, raw_password):
        self.Password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.Password)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

class Faculty(models.Model):
    Designation_Choices = (
        ('Asst.Proffesor', 'Asst.Proffesor'),
        ('Associate ', 'Associate '),
        ('Professor', 'Professor'),
        ('programmer', 'programmer'),
    )

    def generate_faculty_id():
        last_faculty = Faculty.objects.all().order_by('Faculty_Id').last()
        if not last_faculty:
            return 'CCPPF001'
        
        last_id = last_faculty.Faculty_Id
        next_number = int(last_id[6:]) + 1
        return f'CCPPF{next_number:03d}'

    Faculty_Id = models.CharField(max_length=11, primary_key=True, default=generate_faculty_id, editable=False)
    Library_No = models.CharField(max_length=20)
    First_Name = models.CharField(max_length=100)
    Last_Name = models.CharField(max_length=100)
    Email = models.EmailField(unique=True)
    Designation = models.CharField(max_length=50, choices=Designation_Choices)
    Password = models.CharField(max_length=128)  # For storing hashed password

    def __str__(self):
        return f"{self.First_Name} {self.Last_Name} ({self.Faculty_Id})"

    def set_password(self, raw_password):
        self.Password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.Password)

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculties'

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))
    
    class Meta:
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
