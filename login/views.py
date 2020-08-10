from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from . import models
from .forms import UserForm, RegisterForm
from captcha.models import CaptchaStore


# Create your views here.


def login_rqd(func):
    def wrapper(*args):
        if args[0].session.get('is_login', None):
            return func(*args)
        else:
            return redirect('/login/')
    return wrapper


def index(request):
    pass
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None):  # 已经登录了
        return redirect('/index/')

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容"
        if login_form.is_valid():  # 确保用户名和密码都不为空
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == password:  # 通过
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    request.session['email_user'] = user.email
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户名不存在！"
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名不唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址不唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                # return redirect('/login/')  # 自动跳转到登录页面
                return login(request)   # 成功注册之后自动登录

    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/index/')
    request.session.flush()
    # or
    # del request.session['is_login']...

    return redirect('/index/')


@login_rqd
def secret(request):
    return HttpResponse('机密')

