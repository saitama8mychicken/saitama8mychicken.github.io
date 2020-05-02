# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from matplotlib import image
import ast, json
import pandas as pd
from django.conf import settings
from django.shortcuts import render
from CreateRule.forms import UserForm, UserProfileInfoForm
from CreateRule.engine import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from CreateRule.charts import *

def index(request):
    return render(request, 'CreateRule/index.html')
@login_required
def special(request):
    return HttpResponse("You are logged in !")
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                print('found it')
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            registered = True
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request,'CreateRule/registration.html',
                          {'user_form':user_form,
                           'profile_form':profile_form,
                           'registered':registered})
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'CreateRule/login.html', {})


def create_rule(request, code=''):
    if request.method == 'POST':
        # if the request made is to save the code then
        if request.POST.get('save'):
            code = request.POST.get('code')
            out = save_code(code)
            print('saving..')
            return render(request, 'CreateRule/create.html', {'validated': 'True',
                                                              'code': code,
                                                              'output': out,
                                                              'saved': 'True'})
        # if the request made is for sending the inp since code has been verified then execute the input
        if request.POST.get('column'):
            inp = dict()
            column = request.POST.getlist('column')
            type = request.POST.getlist('type')
            code = request.POST.get('code')
            for item, value in zip(column, type):
                inp[item.encode('ascii', 'ignore')] = value.encode('ascii', 'ignore')
            output = evaluate(code, inp)
            return render(request, 'CreateRule/create.html', {'validated': 'True',
                                                                  'code': code,
                                                                  'output': output,
                                                              'input': inp })

        elif request.POST.get('code'):
            code = request.POST.get('code')
            print(code)
            if validate(code):
                out = 'validated'
                return render(request, 'CreateRule/create.html', {'code': code,
                                                                  'validated': 'True'})
            else:
                print(validate(code))
                return render(request, 'CreateRule/create.html', {'code': code,
                                                                  'out': 'false',
                                                                  'validated': 'try_again'})
    else:
        return render(request, 'CreateRule/create.html', {'out': '',
                                                          'validated': 'False',
                                                          'code': code})

def see_rules(request):
    if request.method == 'POST':
        cell = request.POST.get('code')
        print(cell)
        delete_row(cell)
        out = show()
        code = out['code']
        return render(request, 'CreateRule/show.html', {'rule': out['rule'],
                                                        'code': code,
                                                        })
    else:
        out = show()
        code = out['code']
        return render(request, 'CreateRule/show.html', {'rule': out['rule'],
                                                        'code': code,
                                                        })
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        # get the file
        file = request.FILES['file']

        # convert file to csv
        df = pd.read_csv(file)

        # clean the df
        df = clean(df)

        # create dictionary of attributes from df
        dict_file = get_attributes(df)

        # get the output for the passed rules
        output = execute_all(dict_file)

        # convert the output dictionary to a new dict for ease in django template
        # output is a dict having values like {'chart_type':'plot'}
        temp = {}
        url = {}
        for i, d in enumerate(output):
            temp[i] = d
            # print(d)
            url[i] = chart(df, output=d )

        # get all the codes from dictionary
        out = show()
        code = out['code']
        # img = image.imread(settings.MEDIA_ROOT + '/plot/6.png')
        # print(dir(img))
        # img.view()
        return render(request, 'CreateRule/upload.html', {'uploaded': 'True',
                                                          'dict': dict_file,
                                                          'output': temp,
                                                          'code': code,
                                                          'plots': url, })
    else:
        return render(request, 'CreateRule/upload.html', {})

def edit(request):
    if request.method == 'POST':
        pass
    return render(request, 'CreateRule/create.html', {})