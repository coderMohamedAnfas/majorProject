# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.hashers import check_password
# from datetime import datetime
# from .models import Staff, Student

# class CustomAuthenticationBackend(BaseBackend):
#     def authenticate(self, request, phone_number=None, otp=None, admission_no=None, date_of_birth=None, **kwargs):
#         # Staff authentication using phone number and OTP
#         if phone_number and otp:
#             try:
#                 staff = Staff.objects.get(phone_number=phone_number)
#                 if staff.otp == otp:  # Assuming `otp` is a field on the Staff model
#                     return staff
#             except Staff.DoesNotExist:
#                 return None

#         # Student authentication using admission number and date of birth
#         elif admission_no and date_of_birth:
#             print("i am from backend")
#             try:
#                 student = Student.objects.get(admission_no=admission_no)
#                 print("i am from backend1",student)

#                 # Assuming the `password` field on Student is the hashed version of date_of_birth
#                 # Convert date_of_birth string to a datetime object
#                 try:
#                     dob_datetime = datetime.strptime(date_of_birth, '%Y-%m-%d')
#                     print("i am from backend2")

#                 except ValueError:
#                     return None  # Return None if the date format is incorrect
                
#                 # Compare the plain text date_of_birth with the stored password
#                 if check_password(dob_datetime.strftime('%Y-%m-%d'), student.password):
#                     print("i am from backend3",dob_datetime)
#                     print(student.admission_no,student.password)
#                     return student
#             except Student.DoesNotExist:
#                 return None

#         return None

#     def get_user(self, user_id):
#         try:
#             return Staff.objects.get(pk=user_id)
        
#         except Staff.DoesNotExist:
#             try:
#                 # print(Student.objects.get(pk=user_id))
#                 return Student.objects.get(pk=user_id)
#             except Student.DoesNotExist:
#                 return None
# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.hashers import check_password
# from datetime import datetime
# from .models import Staff, Student

# class CustomAuthenticationBackend(BaseBackend):
#     def authenticate(self, request, phone_number=None, password=None, otp=None, admission_no=None, date_of_birth=None, **kwargs):
#         # Staff authentication using phone number and either password or OTP
#         if phone_number:
#             try:
#                 staff = Staff.objects.get(phone_number=phone_number)
                
#                 # Authenticate with password
#                 if password and check_password(password, staff.password):
#                     return staff
                
#                 # Authenticate with OTP
#                 elif otp and staff.otp == otp:  # Assuming `otp` is a field on the Staff model
#                     return staff

#             except Staff.DoesNotExist:
#                 return None

#         # Student authentication using admission number and date of birth
#         elif admission_no and date_of_birth:
#             try:
#                 student = Student.objects.get(admission_no=admission_no)

#                 # Convert date_of_birth string to a datetime object
#                 try:
#                     dob_datetime = datetime.strptime(date_of_birth, '%Y-%m-%d')
#                 except ValueError:
#                     return None  # Return None if the date format is incorrect
                
#                 # Compare the date_of_birth as a password
#                 if check_password(dob_datetime.strftime('%Y-%m-%d'), student.password):
#                     print(f"student is {student.admission_no}")
#                     return student
#             except Student.DoesNotExist:
#                 return None

#         return None

#     def get_user(self, user_id):
#         # Attempt to retrieve the user by ID, trying both Staff and Student models
#         try:
#             return Staff.objects.get(pk=user_id)
#         except Staff.DoesNotExist:
#             try:
#                 return Student.objects.get(pk=user_id)
#             except Student.DoesNotExist:
#                 return None
# CustomAuthenticationBackend.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.utils.timezone import datetime
from .models import Staff, Student
import logging

logger = logging.getLogger(__name__)

class CustomAuthenticationBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, password=None, otp=None, admission_no=None, date_of_birth=None, **kwargs):
        # Staff authentication
        if phone_number:
            try:
                staff = Staff.objects.get(phone_number=phone_number)
                if password and check_password(password, staff.password):
                    return staff
                elif otp and staff.otp == otp:
                    # Add logic to invalidate OTP if necessary
                    return staff
            except Staff.DoesNotExist:
                logger.warning(f"Staff with phone number {phone_number} does not exist.")
                return None
        
        # Student authentication
        elif admission_no and date_of_birth:
            try:
                student = Student.objects.get(admission_no=admission_no)
                try:
                    dob_datetime = datetime.strptime(date_of_birth, '%Y-%m-%d')
                except ValueError:
                    logger.warning(f"Invalid date format for student with admission no {admission_no}.")
                    return None
                
                if check_password(dob_datetime.strftime('%Y-%m-%d'), student.password):
                    return student
            except Student.DoesNotExist:
                logger.warning(f"Student with admission no {admission_no} does not exist.")
                return None

        return None

    def get_user(self, user_id):
        try:
            return Staff.objects.get(pk=user_id)
        except Staff.DoesNotExist:
            try:
                print(Student.objects.get(pk=user_id))
                return Student.objects.get(pk=user_id)
            except Student.DoesNotExist:
                logger.warning(f"User with ID {user_id} does not exist.")
                return None

