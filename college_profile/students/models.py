from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Custom User Manager for Staff
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number=None,password=None,email=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field is required')
        email = self.normalize_email(email)
        
        # Create and save the user with the given phone number, email, and extra fields
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, password=None,email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, email, **extra_fields)

# Custom Student Manager
# class CustomStudentManager(BaseUserManager):
#     def create_user(self, admission_no=None, date_of_birth=None,**extra_fields):
#         if not admission_no:
#             raise ValueError('The Admission Number field is required')
#         if not date_of_birth:
#             raise ValueError('The date_of_birth field is required')
#         user = self.model(admission_no=admission_no,date_of_birth=date_of_birth, **extra_fields)
#         user.set_password(date_of_birth.strftime('%Y-%m-%d'))  # Set DOB as password
#         user.save(using=self._db)
#         return user
from datetime import datetime

class CustomStudentManager(BaseUserManager):
    def create_user(self, admission_no=None, date_of_birth=None, **extra_fields):
        if not admission_no:
            raise ValueError('The Admission Number field is required')
        if not date_of_birth:
            raise ValueError('The date_of_birth field is required')

        # Convert date_of_birth string to a date object if it's a string
        if isinstance(date_of_birth, str):
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        
        user = self.model(admission_no=admission_no, date_of_birth=date_of_birth, **extra_fields)
        user.set_password(date_of_birth.strftime('%Y-%m-%d'))  # Set DOB as password
        user.save(using=self._db)
        return user

    def create_superuser(self, admission_no=None, date_of_birth=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(admission_no, date_of_birth, **extra_fields)


# Student Model
class Student(AbstractUser):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ("Don't Know","Don't Know")
    ]

    username = None
    admission_no = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    full_name = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=20, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    PRN = models.CharField(max_length=20, unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', default='profile_images/avatar.png', blank=True, null=True)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    relation = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    passout_year = models.IntegerField(blank=True,  null=True)
    is_complete = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False,null=True)

    USERNAME_FIELD = 'admission_no'
    REQUIRED_FIELDS = ['date_of_birth']

    groups = models.ManyToManyField(
        Group,
        related_name='student_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='student_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomStudentManager()

    def save(self, *args, **kwargs):
        if all([self.full_name, self.department, self.phone_number, self.address, self.blood_group, self.PRN, self.parent_name, self.gender, self.email, self.passout_year]):
            self.is_complete = True
        else:
            self.is_complete = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.admission_no

# Staff Model
class Staff(AbstractUser):
    DESIGNATION_CHOICES = [
        ('Admin','Admin'),
        ('HOD', 'Head of Department'),
        ('Lecturer', 'Lecturer'),
        ('Tutor', 'Tutor'),
        ('Other','Other')
    ]

    username = None
    phone_number = models.CharField(max_length=15, unique=True)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(default="email@gmail.com")
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['designation','email']

    groups = models.ManyToManyField(
        Group,
        related_name='staff_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='staff_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

# Automatic Department Creation
def create_departments(sender, **kwargs):
    departments = [
        'CIVIL ENGINEERING',
        'COMPUTER HARDWARE ENGINEERING',
        'MECHANICAL ENGINEERING',
        'INSTRUMENTATION ENGINEERING',
        'ELECTRONICS ENGINEERING',
        'ELECTRICAL AND ELECTRONICS ENGINEERING',
    ]
    for department_name in departments:
        Department.objects.get_or_create(name=department_name)

# Connect the signal to automatically create departments when needed
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def ensure_departments_exist(sender, **kwargs):
    create_departments(sender, **kwargs)


