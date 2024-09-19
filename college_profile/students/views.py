import email
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Student, Department,Staff
import csv
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
import pandas as pd
from .models import Student, Department
from datetime import datetime
import os
import zipfile
import tempfile
# from django.http import HttpResponse
# import pandas as pd
# from django.shortcuts import render
# from django.core.files.storage import default_storage
# from .models import Student, Department

import random
from django.core.mail import send_mail

from datetime import timedelta
import django.utils.timezone as tm
from django.utils.timezone import now

def generate_otp():
    return str(random.randint(100000, 999999))

def send_html_via_email(email,otp):
    now = datetime.now()
    
    # Calculate the time 10 minutes later
    ten_minutes_later = now + timedelta(minutes=10)
    
    # Format the times for display
    timefrom = now.strftime('%d-%m-%Y %H:%M')
    timeto = ten_minutes_later.strftime('%d-%m-%Y %H:%M')
    html_message = f"""
    <html>
    <body>
        <h1 style="color: #333;">Welcome to Our Service</h1>
    <p>Hello,</p>
    <p>Your OTP code is <strong>{otp}</strong>. Please use this code to complete your login process.</p>
    <p><strong>Important:</strong> This OTP is valid from <strong>{timefrom}</strong> to <strong>{timeto}</strong>. If the OTP expires, you will need to request a new one.</p>
    
    <p>Thank you,<br>GPTC Palakkad</p>

    </body>
    </html>
    """
    send_mail(subject="Reset Password",message=" Thanks for using this feature",from_email='mohamedanfas7578@gmail.com',recipient_list=[email],html_message=html_message)


def forgot_pass(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        send_html_via_email(email)    
    return render(request,'forgot_password.html')


# Send OTP via email
def send_otp_via_email(otp, email):
    subject = 'Your OTP Code'
    message = (
        f'Your OTP code is {otp}. Please use this to login.\n\n'
        'Note: This OTP is valid for 10 minutes. If it expires, you will need to request a new OTP.'
    )
    try:
        # send_mail(subject, message, 'mohamedanfas7578@gmail.com', [email])
        send_html_via_email(email,otp)    
        print('OTP sent successfully')
    except Exception as e:
        print(f'Failed to send OTP: {e}')
        raise

# Request OTP view
def request_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        try:
            staff = Staff.objects.get(phone_number=phone_number)
            otp = generate_otp()
            staff.otp = otp
            staff.otp_generated_at = now()
            staff.save()

            send_otp_via_email(otp, staff.email)
            messages.success(request, 'OTP sent to your email.')
            return redirect('login')
        except Staff.DoesNotExist:
            messages.error(request, 'Phone number not registered.')
        except Exception as e:
            messages.error(request, f'Failed to send OTP: {str(e)}')
    
    return render(request, 'request_otp.html')



def student_id_preview(request):
    department_id = request.GET.get('department')
    passout_year = request.GET.get('passout_year')
    admission_no = request.GET.get('admission_no')

    students = Student.objects.all()
    if department_id:
        students = students.filter(department_id=department_id)
    if passout_year:
        students = students.filter(passout_year=passout_year)
    if admission_no:
        students = students.filter(admission_no__icontains=admission_no)

    departments = Department.objects.all()
    
    context = {
        'students': students,
        'departments': departments,
        'filter_department': department_id,
        'filter_passout_year': passout_year,
        'filter_admission_no': admission_no,
    }
    return render(request, 'student_id_preview.html', context)

# def student_id_detail(request, pk):
#     student = get_object_or_404(Student, pk=pk)
#     return render(request, 'student_id_detail.html', {'student': student})



def student_management(request):
    return render(request, 'student_management.html')

def staff_management(request):
    departments = Department.objects.all()
    selected_department = request.GET.get('department')
    
    if selected_department:
        staff_members = Staff.objects.filter(department__id=selected_department)
    else:
        staff_members = Staff.objects.all()
    
    return render(request, 'staff_management.html', {
        'departments': departments,
        'staff_members': staff_members,
        'selected_department': selected_department,
    })


def admin_dashboard(request):
    # filter_department = request.GET.get('department')
    # filter_passout_year = request.GET.get('passout_year')
    # departments = Department.objects.all()
    # students = Student.objects.all()

    # if filter_department:
    #     students = students.filter(department_id=filter_department)
    # if filter_passout_year:
    #     students = students.filter(passout_year=filter_passout_year)

    # context = {
    #     'departments': departments,
    #     'students': students,
    #     'filter_department': filter_department,
    #     'filter_passout_year': filter_passout_year,
    # }
    # return render(request, 'admin_dashboard.html', context)
    return render(request, 'admin_dashboard.html')


def custom_login_view(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')

        if user_type == 'student':
            admission_no = request.POST.get('admission_no')
            date_of_birth = request.POST.get('date_of_birth')
            user = authenticate(request, admission_no=admission_no, date_of_birth=date_of_birth)
            print(f"user info from login method {user}")
            if  isinstance(user, Student):
                print(f"User type: {type(user)}") 
                login(request, user)
                return redirect('student_profile')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})

        elif user_type == 'staff':
            phone_number = request.POST.get('phone_number')
            auth_method = request.POST.get('auth_method')
            password = request.POST.get('password')
            otp = request.POST.get('otp')
            
            if auth_method == 'password':
                user = authenticate(request, phone_number=phone_number, password=password)
            elif auth_method == 'otp':
                user = authenticate(request, phone_number=phone_number, otp=otp)

            if user is not None:
                if user.designation == 'Admin':
                    login(request, user)
                    return redirect('admin_dashboard')
                elif user.designation == 'HOD':
                    return redirect('hod_dashboard')
                else:
                    login(request,user)
                    return redirect('staff_profile')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def custom_logout(request):
    logout(request)
    return redirect('login')

def student_profile_view(request):
    if request.method == 'POST':
        user = request.user

        user.full_name = request.POST.get('full_name', user.full_name)
        user.department_id = request.POST.get('department', user.department_id)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.address = request.POST.get('address', user.address)
        user.blood_group = request.POST.get('blood_group', user.blood_group)
        user.PRN = request.POST.get('PRN', user.PRN)
        user.parent_name = request.POST.get('parent_name', user.parent_name)
        user.relation = request.POST.get('relation', user.relation)
        user.gender = request.POST.get('gender', user.gender)
        user.email = request.POST.get('email', user.email)
        user.passout_year = request.POST.get('passout_year', user.passout_year)

        if 'image' in request.FILES:
            if user.image and user.image != 'avatar.png':  # Adjust the condition based on your default image or handle accordingly
                # Delete the old image file
                user.image.delete(save=False)

            user.image = request.FILES['image']
            print(f"Image file: {user.image}")  # Debugging statement
            print(f"Image file name: {request.FILES['image'].name}")

        user.save()
        messages.info(request,"Succesfully Updated Your Profile")
        return redirect('student_profile')
    
    departments = Department.objects.all()
    student = request.user
    print(f"requested user : {request.user}")
    return render(request, 'students/profile.html', {'departments': departments, 'user': student}) 
  
def staff_profile_view(request):
    
    if not request.user.is_authenticated or not isinstance(request.user, Staff):
        return redirect('login')

    # Add any additional logic for staff profile here
    departments = Department.objects.all()

    return render(request, 'staff_profile.html', {'staff': request.user,'departments':departments})


def view_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    departments = Department.objects.all()
    return render(request, 'students/profile.html', {'user': student,'departments': departments,})


def create_student(request):
    if request.method == 'POST':
        admission_no = request.POST.get('admission_no')
        date_of_birth = request.POST.get('date_of_birth')
        print(type(date_of_birth))
        
        if isinstance(date_of_birth, str):
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            print(type(date_of_birth))
        try:
            Student.objects.create_user(
                    admission_no=admission_no,
                    date_of_birth= date_of_birth)
            messages.success(request,"student created")
        except:
            messages.warning(request,"MUST BE VALID CREDITIONALS !!!!!")
    # Logic for creating a student individually
    return render(request, 'student_management.html')


@staff_member_required
def upload_students(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        file_type = file.name.split('.')[-1].lower()
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        filepath = fs.path(filename)

        if file_type == 'csv':
            df = pd.read_csv(filepath)
        elif file_type in ['xls', 'xlsx']:
            df = pd.read_excel(filepath)
        else:
            return render(request, 'admin/upload_students.html', {'error': 'Unsupported file format'})

        for index, row in df.iterrows():
            admission_no = row['Adm No.']
            date_of_birth_str = row['DOB']
            # print(date_of_birth_str)
            # date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            # print(date_of_birth)
            full_name = row.get('Aplicant Name', '')
            parent_name = row.get('Guardian', '')
            relation = row.get('Relation', '')
            address = row.get('Address', '')
            gender = row.get('Gender', '')
            if gender == 'M':
                gender = 'Male'
            elif gender == 'F' :
                gender = 'Female'.upper()

            email = row.get('E-mail', '')
            phone_number = row.get('Mobile', '')
            department_name = str(row.get('Diploma Programme', '')).upper()
            passout_year = row.get('Passout Year', None)

            department = None
            if department_name:
                department, created = Department.objects.get_or_create(name=department_name)

            try:
                Student.objects.create_user(
                    admission_no=admission_no,
                    date_of_birth=date_of_birth_str,
                    full_name=full_name,
                    parent_name=parent_name,
                    relation=relation,
                    address=address,
                    gender=gender,
                    email=email,
                    phone_number=phone_number,
                    department=department,
                    passout_year=passout_year,
                )
            except Exception as e:
                print(f"Error creating student {admission_no}: {e}")

        return redirect('admin_dashboard')

    return render(request, 'admin/upload_students.html')

def create_staff(request):
    if request.method == 'POST':
        phone_number = request.POST.get('ph_no')
        # email = request.POST.get('email')
        pwd = request.POST.get('password')
        desg = request.POST.get('designation')
        email = request.POST.get('email')
        department_id = request.POST.get('department_name')  # Get the department id from the form
        
        try:
            # Fetch the selected department using its id
            department = Department.objects.get(id=department_id)
            s = Staff.objects.create_user(
                    phone_number=phone_number,
                    password=pwd,
                    designation = desg, 
                    email=email,
                    department=department
                    )
            messages.success(request,"staff created")
        except:
            messages.warning(request,"MUST BE VALID CREDITIONALS !!!!!")
    # Logic for creating staff individually
    return redirect('staff_management')

def upload_staff(request):
    if request.method == 'POST':
        # Logic for handling file upload and creating staff
        pass
    return render(request, 'upload_staff.html')

def generate_id_card(request):
    # Logic for generating ID cards
    return render(request, 'generate_id_card.html')

def student_approval_view(request):
    department = request.GET.get('department')
    passout_year = request.GET.get('passout_year')
    admission_no = request.GET.get('admission_no')
    approval_status = request.GET.get('approval_status')

    students = Student.objects.all()

    # Apply filters based on GET parameters
    if department:
        students = students.filter(department_id=department)
    if passout_year:
        students = students.filter(passout_year=passout_year)
    if admission_no:
        students = students.filter(admission_no=admission_no)
    if approval_status:
        if approval_status == 'approved':
            students = students.filter(is_approved=True)
        elif approval_status == 'not_approved':
            students = students.filter(is_approved=False)

    if request.method == "POST":
        if request.POST.get('student_id'):
            # Individual approval or rejection
            student_id = request.POST.get('student_id')
            action = request.POST.get('action')
            student = Student.objects.get(id=student_id)

            if action == 'approve':
                student.is_approved = True
                messages.success(request,f"{student.full_name} Profile Approved Successfully")
                # student.is_complete = True
            elif action == 'reject':
                student.is_approved = False
                messages.warning(request,f"{student.full_name} Profile Rejected Successfully")
                # student.is_complete = False
            
            student.save()

        elif request.POST.getlist('student_ids'):
            # Bulk approval or rejection
            student_ids = request.POST.getlist('student_ids')
            action = request.POST.get('action1')

            if student_ids and action:
                selected_students = Student.objects.filter(id__in=student_ids)

                if action == 'approve':
                    selected_students.update(is_approved=True)
                elif action == 'reject':
                    selected_students.update(is_approved=False)

        return redirect('student_approval')

    return render(request, 'student_approval.html', {
        'students': students,
        'departments': Department.objects.all(),
    })




def home_view(request):
    # Get filtering parameters
    department = request.GET.get('department')
    passout_year = request.GET.get('passout_year')

    # Filter students based on the parameters
    students = Student.objects.all()
    if department:
        students = students.filter(department_id=department)
    if passout_year:
        students = students.filter(passout_year=passout_year)

    if request.method == "POST":
        # Handle the export request
        export_type = request.POST.get('export_type')
        i = 0
        # Create a Pandas DataFrame for the Excel/CSV file
        data = {
            'Full_Name': [student.full_name for student in students],
            'Admission_No': [student.admission_no for student in students],
            'Department': [(student.department.name if student.department else 'N/A') for student in students],
            'Passout_Year': [student.passout_year for student in students],
            'PRN': [student.PRN for student in students],  
            'Blood_Group': [student.blood_group for student in students],  
            'Address': [student.address for student in students],  
            'Parent_name': [student.parent_name for student in students],  
            'Phone_No': [student.phone_number for student in students],  
            'Gender': [student.gender for student in students],  
            'Email': [student.email for student in students],  
            'Date_Of_Birth': [student.blood_group for student in students],  


        }
        df = pd.DataFrame(data)

        # Create a temporary directory for zipping
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the Excel/CSV file in the temporary directory
            if export_type == 'excel':
                file_path = os.path.join(temp_dir, 'students.xlsx')
                df.to_excel(file_path, index=False, engine='openpyxl')
            elif export_type == 'csv':
                file_path = os.path.join(temp_dir, 'students.csv')
                df.to_csv(file_path, index=False)


            # Create a ZIP file with the Excel/CSV and images
            zip_path = os.path.join(temp_dir, 'students_data.zip')
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                # Add the Excel/CSV file to the ZIP
                zip_file.write(file_path, os.path.basename(file_path))

                # Add each student's image to the ZIP
                for student in students:
                    if student.image:
                        image_path = student.image.path
                        unique_image_name = f'{student.admission_no}.jpg'  # Rename image with unique ID
                        zip_file.write(image_path, unique_image_name)

            # Prepare the ZIP file for download
            with open(zip_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=students_data.zip'
                return response

    # Render the home page with filtering options
    return render(request, 'home.html', {
        'departments': Department.objects.all(),
        'students': students,
    })


def approve_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_approved = True
    student.save()
    return redirect('admin_dashboard')



def reject_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_approved = False
    student.save()
    return redirect('admin_dashboard')