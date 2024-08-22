from django.urls import path
from . import  views

urlpatterns = [
    # login
    path('login/', views.custom_login_view, name='login'),
    # to profile pages
    path('student/profile/', views.student_profile_view, name='student_profile'),
    path('staff/profile/', views.staff_profile_view, name='staff_profile'),
    # to admin dashboard
    path('admin/home/',views.home_view,name='home'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/profile/',views.admin_dashboard,name="profile"),
    path('logout/',views.custom_logout,name="logout"),
    # to control on students
    path('admin/student/view/<int:student_id>/', views.view_student, name='view_student'),
   
    
    
    path('student_management/', views.student_management, name='student_management'),
    path('create_student/', views.create_student, name='create_student'),
    path('upload_students/', views.upload_students, name='upload_students'),

    path('staff_management/', views.staff_management, name='staff_management'), 
    path('create_staff/', views.create_staff, name='create_staff'), 

    path('id_card_generation/', views.generate_id_card, name='id_card_generation'),

    path('student_id_preview/', views.student_id_preview, name='student_id_preview'),
    # path('student_id_detail/<int:pk>/', views.student_id_detail, name='student_id_detail')
  path('student_approval/', views.student_approval_view, name='student_approval'),

     path('request_otp/', views.request_otp, name='request_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
]


