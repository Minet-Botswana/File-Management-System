from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from fms_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from fmsApp.forms import UserRegistration, SavePost, UpdateProfile, UpdatePasswords
from fmsApp.models import Post
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from fmsApp.models import Post, Company, Department, DepartmentUser, Department, DepartmentUser
from django.http import JsonResponse
#from .models import File  # Assuming you have a File model
# Create your views here.

context = {
    'page_title' : 'File Management System',
}
#login
'''
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')
'''
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import json

def login_user(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.groups.filter(name='staff_admin').exists():
                    resp['status'] = 'success'
                    # Redirect staff users to their dashboard
                    return HttpResponse(json.dumps(resp), content_type='application/json')
                else:
                    resp['msg'] = "You are not authorized to access this dashboard."
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type='application/json')



#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')

@login_required
def home(request):
    context['page_title'] = 'Home'
    if request.user.is_superuser:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(user = request.user).all()
    context['posts'] = posts
    context['postsLen'] = posts.count()
    print(request.build_absolute_uri())
    return render(request, 'home.html',context)

def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html',context)

@login_required
def posts_mgt(request):
    context['page_title'] = 'Uploads'

    #posts = Post.objects.filter(user = request.user).order_by('title', '-date_created').all()
    posts = Post.objects.order_by('title', '-date_created').all()
    context['posts'] = posts
    print(posts)
    return render(request, 'posts_mgt.html', context)
'''
@login_required
def manage_post(request, pk=None):
    context['page_title'] = 'Manage Post'
    context['post'] = {}
    if not pk is None:
        post = Post.objects.get(id=pk)
        context['post'] = post
    companies = Company.objects.all()
    departments = Department.objects.all()
    users = User.objects.filter(groups__name='staff')
    context['companies'] = companies
    context['departments'] = departments
    context['users'] = users
    return render(request, 'manage_post.html', context)
'''
from django.contrib.auth.decorators import login_required

@login_required
def manage_post(request, pk=None):
    context['page_title'] = 'Manage Post'
    context['post'] = {}
    if pk is not None:
        post = Post.objects.get(id=pk)
        context['post'] = post
    companies = Company.objects.all()
    departments = Department.objects.all()
    users = User.objects.none()  # Initialize an empty queryset
    if request.method == 'POST' and 'department' in request.POST:
        # If a department is selected in the form, filter users based on that department
        department_id = request.POST.get('department')
        department = Department.objects.get(pk=department_id)
        users = User.objects.filter(departmentuser__department=department)
    context['companies'] = companies
    context['departments'] = departments
    context['users'] = users
    return render(request, 'manage_post.html', context)


@login_required
def save_post(request):
    resp = {'status':'failed', 'msg':''}
    if request.method == 'POST':
        if not request.POST['id'] == '':
            post = Post.objects.get(id=request.POST['id'])
            form = SavePost(request.POST,request.FILES,instance=post)
        else:
            form = SavePost(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'File has been saved successfully.')
            resp['status'] = 'success'
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str( error +'<br/>')
            form = SavePost(request.POST,request.FILES)
            
    else:
        resp['msg'] = "No Data sent."
    print(resp)
    return HttpResponse(json.dumps(resp),content_type="application/json")

@login_required
def delete_post(request):
    resp = {'status':'failed', 'msg':''}
    if request.method == 'POST':
        try:
            post = Post.objects.get(id = request.POST['id'])
            post.delete()
            resp['status'] = 'success'
            messages.success(request, 'Post has been deleted successfully')
        except:
           resp['msg'] = "Undefined Post ID"
    return HttpResponse(json.dumps(resp),content_type="application/json")

def shareF(request,id=None):
    # print(str("b'UdhnfelTxqj3q6BbPe7H86sfQnboSBzb0irm2atoFUw='").encode())
    context['page_title'] = 'Shared File'
    if not id is None:
        key = settings.ID_ENCRYPTION_KEY
        fernet = Fernet(key)
        id = base64.urlsafe_b64decode(id)
        id = fernet.decrypt(id).decode()
        post = Post.objects.get(id = id)
        context['post'] = post
        context['page_title'] += str(" - " + post.title)
   
    return render(request, 'share-file.html',context)

@login_required
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)


def get_departments(request):
    company_id = request.GET.get('company_id')
    departments = Department.objects.filter(company_id=company_id).values('id', 'name')
    return JsonResponse({'departments': list(departments)})

def get_users(request):
    department_id = request.GET.get('department_id')
    department_users = DepartmentUser.objects.filter(department_id=department_id)
    users = User.objects.filter(id__in=department_users.values('user_id')).values('id', 'first_name', 'last_name', 'username')
    print(users)
    return JsonResponse({'users': list(users)})


from django.shortcuts import render
from .models import Post, DepartmentUser

def staff_home(request):
    # Get the departments associated with the current user
    user_departments = DepartmentUser.objects.filter(user=request.user)

    # Extract department IDs
    department_ids = user_departments.values_list('department_id', flat=True)

    # Get all posts belonging to the departments associated with the user
    posts = Post.objects.filter(department_id__in=department_ids)

    # Pass posts data to the template
    context = {
        'posts': posts
    }

    # Render the template with posts data
    return render(request, 'staff_home.html', context)



