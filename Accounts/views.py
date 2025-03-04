from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def login_view(request):


    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            # Log in the user
            login(request, user)
            return redirect('import_student_data')  # Redirect to the import page or any other page after login
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')  # Show error message if authentication fails

    return render(request, 'accounts/login.html')

# def register(request):
#     return render(request, 'accounts/register.html')


def user_logout(request):
    logout(request)  # This will clear the session and log the user out
    return redirect('login') 