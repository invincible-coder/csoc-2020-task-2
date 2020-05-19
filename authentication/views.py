from django.shortcuts import render
from django.contrib.auth import login,logout,authenticate
# Create your views here.
from django.shortcuts import redirect,render
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.http import HttpResponse

def loginView(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        username = request.POST['Username']
        password =  request.POST['Password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            return render(request,'login.html',{'message':"Invalid Credentials"})
    else:
        return render(request, 'login.html',{'msg':"Invalid request method"})
    

def logoutView(request):
    logout(request)
    return redirect('index')

def registerView(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            login(request,user)
            return redirect('index')
                                                    
    else:
        return render(request, 'register.html', {'form':RegisterForm(), 'error':'Invalid Request'})

