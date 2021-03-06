from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import UserForm,UploadFileForm
from .models import UserProfile, CategoriesQ , Ins, Questions
from django.db import connection
import locale
import os, filecmp
from django import forms

# Create your views here.
codes = {200:'success',404:'file not found',400:'error',408:'timeout'}

def home(request):
    if not request.user.is_authenticated():
        return render(request, 'avs/login.html')
    else:
        dic = []
        ccx=0
        s = []
        for i in CategoriesQ.objects.all():
            s.append(i)
            ccx = ccx + 1
            if ccx % 3 == 0:
                dic.append(s)
                s = []
        if not ccx % 3 == 0:
            dic.append(s)
        return render(request, 'avs/home_new.html', {"dic":dic})

def QuestionsList(request, Cid):
    category = get_object_or_404(CategoriesQ, pk=Cid)
    cursor = connection.cursor()
    c = category.Cid
    n = category.Name
    cursor.execute("Select avs_Questions.id as ID,avs_Questions.Name as NAM,avs_Questions.Difficulty as DIFF, \
        avs_Questions.Time_Limit as TL, avs_Questions.Memory_Limit as ML from avs_Questions,avs_Ins,avs_CategoriesQ \
        where avs_CategoriesQ.Cid= avs_Ins.category_id and \
        avs_Questions.id=avs_Ins.questions_id and avs_CategoriesQ.Cid=%s",[c])
    X = cursor.fetchall()
    return render(request, 'avs/questionsList.html',{'list':X, 'Cname':n})

def scoreboard(request):
    cursor = connection.cursor()
    cursor.execute("Select username as Name, score / 100 as QuestionsSolved, score as Score from avs_userprofile, auth_user where avs_userprofile.id = auth_user.id")
    X =cursor.fetchall()
    return render(request, 'avs/scoreboard.html', {'x': X})


def compile(request, Qid, lan):

    question = get_object_or_404(Questions, pk=Qid)
    cursor = connection.cursor()
    c = question.id
    cursor.execute("Select inputTestFile,outputTestFile,Time_Limit \
     from avs_questions,avs_testcase where avs_questions.id=%s",[c])
    X = cursor.fetchall()
    m = []
    TimeL = 0
    for i in X:
        inp = i[0]
        out = i[1]
        tl = i[2]
        TimeL = tl
        with open(inp,'r',encoding=locale.getpreferredencoding()) as a_file:
            a_content = a_file.read()
            with open('Testcase0.txt','w',encoding=locale.getpreferredencoding()) as b_file:
                b_file.write(a_content)

        with open(out,'r',encoding=locale.getpreferredencoding()) as a_file:
            a_content = a_file.read()
            with open('TestcaseOut0.txt','w',encoding=locale.getpreferredencoding()) as b_file:
                b_file.write(a_content) 

        file = 'sub.'+lan
        lang = lan
        testin = 'Testcase0.txt'
        testout = 'TestcaseOut0.txt'
        timeout = str(tl) # secs

        c = codes[compile1(file,lan)]
        r = codes[run('sub',testin,timeout,lang)]
        m.append(match(testout))
    x = True
    for i in m:
        if m is False:
            x = False
    fil = "sub."+lan

    s = 0
    if x is True:
        s = 100

    cursor.execute("Insert into avs_submission (time_taken,time_limit,language,score,Qid_id,Uid_id,Code) \
        values (%s,0.2,%s,%s,%s,%s,%s)",([TimeL],[lan],[s],[Qid],[request.user.id],[fil]))
    cursor.execute("Select score from avs_userprofile where id = %s",[request.user.id])
    e = cursor.fetchall()
    d = str(int(s) + int(e[0][0]))
    cursor.execute("select count(*) from avs_solved where questions_id = %s and users_id = %s",([Qid],[request.user.id]))
    count = cursor.fetchall()[0]
    if count[0]==0 and x is True:
        cursor.execute("update avs_userprofile set score = %s where id = %s",([d],[request.user.id]))
        cursor.execute("insert into avs_solved (questions_id,users_id)\
         values (%s,%s)",([Qid],[request.user.id]))
    return render(request, 'avs/compile.html',{'verdict':m , 'answer':x,'count':count})




def QuestionSolve(request, Qid):
    question = get_object_or_404(Questions, pk=Qid)
    cursor = connection.cursor()
    c = question.id
    cursor.execute("Select avs_Questions.Name,avs_Questions.ProblemStatement, \
    avs_Questions.InputFormat,avs_Questions.OutputFormat,avs_Questions.Constraints,\
    avs_Questions.SampleInput,avs_Questions.SampleOutput,avs_Questions.Memory_limit, \
    avs_Questions.Time_limit from avs_Questions where avs_Questions.id=%s",[c])
    X = cursor.fetchall()
    # t = X[0][1]
    # f = open(t)
    # stat = f.read()
    # f.close()
    if request.method == 'POST':
        form = UploadFileForm(request.POST,request.FILES)
        if form.is_valid():
            lan = form.cleaned_data['Language']
            if (lan != 'cpp') and (lan != 'java') and (lan != 'c'):
                form.errors['invalid_language'] = 'Please enter a valid language extension!'
                return render(request, 'avs/questionSolve.html',{'list':X,'form':form})            

            filename = request.FILES['Code'].name

            if lan == 'java':
                if filename[-4:] != 'java':
                    form.errors['match_error'] = 'File extension does not match with the language extension!'
                    return render(request, 'avs/questionSolve.html',{'list':X,'form':form}) 

            if lan == 'cpp':
                if filename[-3:] != 'cpp':
                    form.errors['match_error'] = 'File extension does not match with the language extension!'
                    return render(request, 'avs/questionSolve.html',{'list':X,'form':form}) 

            if lan == 'c':
                if filename[-1:] != 'c':
                    form.errors['match_error'] = 'File extension does not match with the language extension!'
                    return render(request, 'avs/questionSolve.html',{'list':X,'form':form}) 

            handle_uploaded_file(request.FILES['Code'],lan)

            return HttpResponseRedirect('/compile/'+Qid + '/' + lan+'/')
    else:
        form = UploadFileForm()
    return render(request, 'avs/questionSolve.html',{'list':X,'form':form})

def handle_uploaded_file(f,lan):
    with open('sub.'+lan,'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('avs:home')
            else:
                return render(request, 'avs/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'avs/login.html', {'error_message': 'Invalid login'})
    return render(request, 'avs/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        userprofile = UserProfile(user=user,score=0)
        userprofile.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                #albums = Album.objects.filter(user=request.user)
                return redirect('avs:home')
    context = {
        "form": form,
    }
    return render(request, 'avs/register.html', context)


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'avs/login.html', context)

#compiler

def compile1(file,lang):
    if lang == 'java':
        class_file = file[:-4]+"class"
    elif lang == 'c':
        class_file = file[:-2]
    elif lang=='cpp':
        class_file = file[:-4]

    if (os.path.isfile(class_file)):
        os.remove(class_file)
    if (os.path.isfile(file)):
        if lang == 'java':
            os.system('javac '+file)
        elif lang == 'c' or lang == 'cpp':
            os.system('g++ '+file+' -o '+class_file)
        if (os.path.isfile(class_file)):
            return 200
        else:
            return 400
    else:
        return 404

def run(file,input,timeout,lang):
    if lang == 'java':
        cmd = 'java '+file
    elif lang=='c' or lang=='cpp':
        cmd = './'+file
    r = os.system('timeout '+timeout+' '+cmd+' < '+input+' > out.txt')
    if lang == 'java':
        os.remove(file+'.class')
    elif lang == 'c' or lang == 'cpp':
        os.remove(file)
    if r==0:
        return 200
    elif r==31744:
        os.remove('out.txt')
        return 408
    else:
        os.remove('out.txt')
        return 400

def match(output):
    if os.path.isfile('out.txt') and os.path.isfile(output):
        b = filecmp.cmp('out.txt',output)
        #os.remove('out.txt')
        return b
    else:
        return 404
