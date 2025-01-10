from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from .models import Students, OTP, Faculty
import random
import os
from email.utils import make_msgid
from django.conf import settings

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(first_name, last_name, email, otp):
    try:
        # Create the email message
        subject = 'PowerPitch - Your OTP for Email Verification'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        # Get the logo path
        logo_path = os.path.join(settings.BASE_DIR, 'powerpitch', 'static', 'images', 'plogo.png')
        
        # Create MIMEMultipart message
        msg = EmailMultiAlternatives(subject, '', from_email, recipient_list)
        
        # Get the HTML template
        html_content = render_to_string('email/otp_email.html', {
            'first_name': first_name,
            'last_name': last_name,
            'otp': otp,
        })

        # Add inline image
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                logo_cid = make_msgid()[1:-1]  # strip < and >
                msg.attach('logo.png', logo_data, 'image/png')
                html_content = html_content.replace('{% static "images/plogo.png" %}', f'cid:{logo_cid}')
        
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise

def student_signup_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'get_otp':
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')
            
            # Check if student already exists
            existing_student = Students.objects.filter(Gmail=email).first()
            if existing_student:
                messages.info(request, f"Hey {existing_student.First_Name} ({existing_student.Student_Id}), you already have an account!")
                return redirect('login')
            
            try:
                # Rest of your OTP generation code...
                otp = generate_otp()
                
                # Delete any existing OTP for this email
                OTP.objects.filter(email=email).delete()
                
                # Create new OTP entry with timestamp
                new_otp = OTP.objects.create(
                    email=email,
                    otp=otp,
                    created_at=timezone.now()
                )
                new_otp.save()
                
                # Send OTP via email
                send_otp_email(first_name, last_name, email, otp)
                
                # Store user details in session
                request.session['first_name'] = first_name
                request.session['last_name'] = last_name
                request.session['email'] = email
                
                messages.success(request, 'OTP sent successfully. Please check your email.')
                return render(request, 'SignUp.html', {
                    'otp_sent': True,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                })
                
            except Exception as e:
                messages.error(request, f'Failed to send OTP: {str(e)}')
                return render(request, 'SignUp.html', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                })
            
        elif action == 'verify_otp':
            otp = request.POST.get('otp')
            email = request.session.get('email')
            first_name = request.session.get('first_name')
            last_name = request.session.get('last_name')
            
            try:
                # Get the latest OTP for this email
                otp_obj = OTP.objects.filter(email=email).latest('created_at')
                
                # Check if OTP is expired (10 minutes)
                time_difference = timezone.now() - otp_obj.created_at
                if time_difference.total_seconds() > 600:  # 10 minutes = 600 seconds
                    # Delete expired OTP
                    otp_obj.delete()
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return render(request, 'SignUp.html', {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email
                    })
                
                if otp_obj.otp == otp:
                    # OTP verified successfully
                    messages.success(request, 'Email verified! Please complete your registration.')
                    return render(request, 'SignUp.html', {
                        'otp_verified': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email
                    })
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
                    return render(request, 'SignUp.html', {
                        'otp_sent': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email
                    })
            except OTP.DoesNotExist:
                messages.error(request, 'OTP expired or not found. Please request a new one.')
                return render(request, 'SignUp.html', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                })
            
        elif action == 'signup':
            try:
                first_name = request.session.get('first_name')
                last_name = request.session.get('last_name')
                email = request.session.get('email')
                gender = request.POST.get('gender')
                branch = request.POST.get('branch')
                roll_no = request.POST.get('rollNo')
                year = request.POST.get('year')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirmPassword')
                
                # Validate passwords
                if not password or not confirm_password:
                    messages.error(request, 'Both password fields are required.')
                    return render(request, 'SignUp.html', {
                        'otp_verified': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email
                    })
                
                if password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'SignUp.html', {
                        'otp_verified': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email
                    })
                
                # Create new student
                student = Students.objects.create(
                    First_Name=first_name,
                    Last_Name=last_name,
                    Gmail=email,
                    Gender=gender,
                    Branch=branch,
                    Roll_No=roll_no,
                    Year=year
                )
                
                # Set the password
                student.set_password(password)
                student.save()
                
                # Clear session data and OTP
                OTP.objects.filter(email=email).delete()
                request.session.flush()
                
                messages.success(request, 'Registration successful!')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'SignUp.html', {
                    'otp_verified': True,
                    'first_name': request.session.get('first_name'),
                    'last_name': request.session.get('last_name'),
                    'email': request.session.get('email')
                })
    
    return render(request, 'SignUp.html')

def faculty_signup_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'get_otp':
            first_name = request.POST.get('firstName')
            last_name = request.POST.get('lastName')
            email = request.POST.get('email')
            
            # Check if faculty already exists
            existing_faculty = Faculty.objects.filter(Email=email).first()
            if existing_faculty:
                messages.info(request, f"Hey {existing_faculty.First_Name} ({existing_faculty.Faculty_Id}), you already have an account!")
                return redirect('login')
            
            try:
                # Rest of your OTP generation code...
                otp = generate_otp()
                
                # Delete any existing OTP for this email
                OTP.objects.filter(email=email).delete()
                
                # Create new OTP entry with timestamp
                new_otp = OTP.objects.create(
                    email=email,
                    otp=otp,
                    created_at=timezone.now()
                )
                new_otp.save()
                
                # Send OTP via email
                send_otp_email(first_name, last_name, email, otp)
                
                # Store user details in session
                request.session['first_name'] = first_name
                request.session['last_name'] = last_name
                request.session['email'] = email
                
                messages.success(request, 'OTP sent successfully. Please check your email.')
                return render(request, 'SignUp.html', {
                    'otp_sent': True,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                })
                
            except Exception as e:
                messages.error(request, f'Failed to send OTP: {str(e)}')
                return render(request, 'SignUp.html', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email
                })
        
            
        elif action == 'verify_otp':
            otp = request.POST.get('otp')
            email = request.session.get('email')
            first_name = request.session.get('first_name')
            last_name = request.session.get('last_name')
            
            try:
                # Get the latest OTP for this email
                otp_obj = OTP.objects.filter(email=email).latest('created_at')
                
                # Check if OTP is expired (10 minutes)
                time_difference = timezone.now() - otp_obj.created_at
                if time_difference.total_seconds() > 600:  # 10 minutes = 600 seconds
                    # Delete expired OTP
                    otp_obj.delete()
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return render(request, 'SignUp.html', {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_faculty': True
                    })
                
                if otp_obj.otp == otp:
                    # OTP verified successfully
                    messages.success(request, 'Email verified! Please complete your registration.')
                    return render(request, 'SignUp.html', {
                        'otp_verified': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_faculty': True
                    })
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
                    return render(request, 'SignUp.html', {
                        'otp_sent': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_faculty': True
                    })
            except OTP.DoesNotExist:
                messages.error(request, 'OTP expired or not found. Please request a new one.')
                return render(request, 'SignUp.html', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_faculty': True
                })
            
        elif action == 'signup':
            try:
                first_name = request.session.get('first_name')
                last_name = request.session.get('last_name')
                email = request.session.get('email')
                library_no = request.POST.get('libraryNo')
                designation = request.POST.get('designation')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirmPassword')
                
                # Validate passwords
                if not password or not confirm_password:
                    messages.error(request, 'Both password fields are required.')
                    return render(request, 'SignUp.html', {
                        'otp_verified': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_faculty': True
                    })
                
                if password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'SignUp.html', {
                        'otp_verified': True,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'is_faculty': True
                    })
                
                # Create new faculty
                faculty = Faculty.objects.create(
                    First_Name=first_name,
                    Last_Name=last_name,
                    Email=email,
                    Library_No=library_no,
                    Designation=designation
                )
                
                # Set the password
                faculty.set_password(password)
                faculty.save()
                
                # Clear session data and OTP
                OTP.objects.filter(email=email).delete()
                request.session.flush()
                
                messages.success(request, 'Faculty registration successful!')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'SignUp.html', {
                    'otp_verified': True,
                    'first_name': request.session.get('first_name'),
                    'last_name': request.session.get('last_name'),
                    'email': request.session.get('email'),
                    'is_faculty': True
                })
    
    return render(request, 'SignUp.html', {'is_faculty': True})

def index(request, user_id=None):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    return render(request, 'index.html', {'user_id': user_id})

def login_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'password_login':
            identifier = request.POST.get('identifier')
            password = request.POST.get('password')
            
            # Try to find user by Gmail or CCPP ID
            student = None
            faculty = None
            
            if '@' in identifier:  # Email login
                student = Students.objects.filter(Gmail=identifier).first()
                if not student:
                    faculty = Faculty.objects.filter(Email=identifier).first()
            else:  # CCPP ID login
                student = Students.objects.filter(Student_Id=identifier).first()
                if not student:
                    faculty = Faculty.objects.filter(Faculty_Id=identifier).first()
            
            user = student or faculty
            
            if user and user.check_password(password):
                # Store user info in session
                # Store user info directly in session
                user_id = user.Student_Id if student else user.Faculty_Id
                request.session['user_id'] = user_id
                request.session['first_name'] = user.First_Name
                request.session['last_name'] = user.Last_Name
                request.session['user_type'] = 'Student' if student else 'Faculty'
                return render(request, 'home.html', {'user_id': user_id})
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
                
        elif action == 'get_otp':
            email = request.POST.get('email')
            
            # Check if user exists
            student = Students.objects.filter(Gmail=email).first()
            faculty = Faculty.objects.filter(Email=email).first()
            user = student or faculty
            
            if not user:
                messages.error(request, 'No account found with this email.')
                return render(request, 'login.html', {'otp_mode': True})
            
            try:
                # Generate OTP
                otp = generate_otp()
                
                # Delete any existing OTP for this email
                OTP.objects.filter(email=email).delete()
                
                # Create new OTP entry
                new_otp = OTP.objects.create(
                    email=email,
                    otp=otp,
                    created_at=timezone.now()
                )
                
                # Send OTP via email
                send_otp_email(user.First_Name, user.Last_Name, email, otp)
                
                messages.success(request, 'OTP sent successfully. Please check your email.')
                return render(request, 'login.html', {
                    'otp_mode': True,
                    'otp_sent': True,
                    'email': email
                })
                
            except Exception as e:
                messages.error(request, f'Failed to send OTP: {str(e)}')
                return render(request, 'login.html', {'otp_mode': True})
            
        elif action == 'verify_otp':
            email = request.POST.get('email')
            otp = request.POST.get('otp')
            
            try:
                # Get the latest OTP for this email
                otp_obj = OTP.objects.filter(email=email).latest('created_at')
                
                # Check if OTP is expired (10 minutes)
                time_difference = timezone.now() - otp_obj.created_at
                if time_difference.total_seconds() > 600:
                    otp_obj.delete()
                    messages.error(request, 'OTP has expired. Please request a new one.')
                    return render(request, 'login.html', {
                        'otp_mode': True,
                        'email': email
                    })
                
                if otp_obj.otp == otp:
                    # Find user
                    student = Students.objects.filter(Gmail=email).first()
                    faculty = Faculty.objects.filter(Email=email).first()
                    user = student or faculty
                    
                    if user:
                        # Store user info in session
                        user_id = user.Student_Id if student else user.Faculty_Id
                        request.session['user_id'] = user_id
                        request.session['first_name'] = user.First_Name
                        request.session['last_name'] = user.Last_Name
                        request.session['user_type'] = 'Student' if student else 'Faculty'
                        otp_obj.delete()
                        return render(request, 'home.html', {'user_id': user_id})
                    else:
                        messages.error(request, 'User not found.')
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
                    
                return render(request, 'login.html', {
                    'otp_mode': True,
                    'otp_sent': True,
                    'email': email
                })
                
            except OTP.DoesNotExist:
                messages.error(request, 'OTP expired or not found. Please request a new one.')
                return render(request, 'login.html', {
                    'otp_mode': True,
                    'email': email
                })
    return render(request, 'login.html')

def home(request, user_id=None):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    return render(request, 'home.html', {'user_id': user_id})

def logout_view(request):
    # Clear the user session
    if 'user_info' in request.session:
        del request.session['user_info']
    # Redirect to home page
    return redirect('index')

def profile_view(request, user_id=None):
    if not request.session.get('user_id'):
        return redirect('login')
    user_id = request.session.get('user_id')
    user = Students.objects.get(Student_Id=user_id)
    return render(request, 'profile.html', {'user': user, 'user_id': user_id})

