from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.shortcuts import redirect
from .form import Userform
from .models import Profile, Problem, Synced, Follow
import os
import requests
from html.parser import HTMLParser
from urllib import parse
import urllib.request

user = None
html = None
userPersonalInformation = {}
currentProblem = None
progress = {'numerator': 1, 'denominator': 0}


class ProblemLinkFinder(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.problemLinks = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    if url.find('http://www.spoj.com/status/') == 0 and url.find('/,') == -1 and url.find(
                                    'http://www.spoj.com/status/' + userPersonalInformation['username']) == -1:
                        self.problemLinks.add(url)

    def error(self, message):
        print('Error')

    def getLinks(self):
        return self.problemLinks


def ExtractCode(linkToCode, problemName, line):
    global user
    global userPersonalInformation
    global currentProblem
    global progress
    print('Downloading Code for problem ' + problemName + ': ')
    '''if currentProblem != problemName:
        progress['numerator'] += 1
        currentProblem = problemName
    elif i is i:
        progress['numerator'] += 1'''
    res = user.get(linkToCode)
    res = str(res.content)
    res1 = res.split('<textarea rows="20" cols="70" name="file" id="file" style="width: 100%;" data-input-file="1">')
    res2 = res1[1].split('</textarea>')
    res2[0] = res2[0].replace('\\n', '\n')
    res2[0] = res2[0].replace('\\t', '\t')
    res2[0] = res2[0].replace("\\'", "'")
    code = res2[0]
    sync = Synced.objects.create(user=userPersonalInformation['username'])
    sync.problem = problemName
    sync.time = line[10]
    sync.memory = line[12]
    sync.date = line[4] + ',' + line[3]
    sync.save()
    if not os.path.exists('main/static/solutions/' + problemName):
        os.makedirs('main/static/solutions/' + problemName)
        f = open('main/static/solutions/' + problemName + 'data', 'w')
        f.close()
        problem = Problem.objects.create(name=problemName)
        problem.time = float(line[10])
        problem.memory = int(line[12])
        problem.user = userPersonalInformation['username']
        problem.save()
    soln = 1
    f = open('main/static/solutions/' + problemName + '/data.txt', 'a')
    while os.path.isfile('main/static/solutions/' + problemName + '/' + userPersonalInformation[
        'username'] + '_$$' + str(soln) + '.txt'):
        soln += 1
    file = open(
        'main/static/solutions/' + problemName + '/' + userPersonalInformation['username'] + '_$$' + str(soln) + '.txt',
        'w')
    problem = Problem.objects.get(name=problemName)
    if float(line[10]) < problem.time:
        problem.time = float(line[10])
        problem.memory = int(line[12])
        problem.user = userPersonalInformation['username']
        problem.save()
    elif float(line[10]) == problem.time and int(line[12]) < problem.memory:
        problem.time = float(line[10])
        problem.memory = int(line[12])
        problem.user = userPersonalInformation['username']
        problem.save()
    for i in range(16):
        line[i] = line[i].replace('-', '')
        line[i] = line[i].replace(':', '')
        f.write(line[i])
    f.write('\n')
    f.close()
    file.write(code)
    file.close()
    print('Solution to problem ' + problemName + ' synced')


class LinkToAcceptedSolution(HTMLParser):
    def __init__(self, base_url, problemName, i):
        super().__init__()
        self.base_url = base_url
        self.next = 0
        self.memory = 0
        self.lang = 0
        self.readData = 0
        self.problemName = problemName
        self.i = i
        self.inSpanreadData = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and self.next == 1:
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    print('Downloading Code for problem ' + self.problemName + ': ')
                    ExtractCode(url, self.problemName, self.i)
            self.next = 0
        if tag == 'td' and self.memory == 1:
            for (attribute, value) in attrs:
                if attribute == 'class' and value == 'smemory statustext text-center':
                    self.readData = 1
        if tag == 'td' and self.lang == 1:
            for (attribute, value) in attrs:
                if attribute == 'class' and value == 'slang text-center':
                    self.inSpanreadData = 1
        if tag == 'span' and self.inSpanreadData == 1 and self.lang == 1:
            self.readData = 1
            self.inSpanreadData = 0

    def handle_data(self, data):
        if data == 'accepted':
            self.next = 1
            self.memory = 1
            self.lang = 1
        if self.readData == 1 and self.memory == 1:
            data = data.replace('\\n', '')
            data = data.replace('\\t', '')
            data = data.replace(' ', '')
            print('With Memory: ' + data)
            self.memory = 0
            self.readData = 0
        if self.readData == 1 and self.lang == 1:
            print('In Language: ' + data)
            self.lang = 0
            self.readData = 0

    def error(self, message):
        pass


class FetchPersonalInfo(HTMLParser):
    global userPersonalInformation

    def __init__(self):
        super().__init__()
        self.input = 0
        self.email = 0
        self.nick_name = 0
        self.first_name = 0
        self.last_name = 0
        self.birthyear = 0
        self.city = 0
        self.img = 0
        self.school = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            self.input = 1
        if tag == 'img':
            if self.img == 0:
                self.img = 1
        for (attribute, value) in attrs:
            if attribute == 'src' and self.img == 1 and value.find('gravatar') != -1:
                userPersonalInformation['img'] = value
                self.img = -1
            if attribute == 'name' and value == 'email':
                self.email = 1
            if attribute == 'name' and value == 'school':
                self.school = 1
            if attribute == 'name' and value == 'name':
                self.c_name = 1
            if attribute == 'name' and value == 'firstname':
                self.first_name = 1
            if attribute == 'name' and value == 'lastname':
                self.last_name = 1
            if attribute == 'name' and value == 'birthyear':
                self.birthyear = 1
            if attribute == 'name' and value == 'city':
                self.city = 1
            if attribute == 'value' and self.input == 1 and self.email == 1:
                userPersonalInformation['email'] = value
                self.email = 0
            if attribute == 'value' and self.input == 1 and self.nick_name == 1:
                userPersonalInformation['nick_name'] = value
                self.nick_name = 0
            if attribute == 'value' and self.input == 1 and self.first_name == 1:
                userPersonalInformation['first_name'] = value
                self.first_name = 0
            if attribute == 'value' and self.input == 1 and self.last_name == 1:
                userPersonalInformation['last_name'] = value
                self.last_name = 0
            if attribute == 'value' and self.input == 1 and self.birthyear == 1:
                userPersonalInformation['birthyear'] = value
                self.birthyear = 0
            if attribute == 'value' and self.input == 1 and self.city == 1:
                userPersonalInformation['city'] = value
                self.city = 0
            if attribute == 'value' and self.input == 1 and self.school == 1:
                userPersonalInformation['school'] = value
                self.school = 0

    def handle_data(self, data):
        pass

    def handle_endtag(self, tag):
        if tag == 'input':
            self.input = 0

    def error(self, message):
        pass


def getSignedList(username):
    global user
    res = user.get('http://www.spoj.com/status/' + username + '/signedlist/')
    f = open('s.txt', 'w')
    res = str(res.content)
    res = res.replace('\\n', '\n')
    f.write(res)
    f.close()


def downloadCodes(username):
    global currentProblem
    global progress
    global userPersonalInformation
    getSignedList(username)
    fin = open("s.txt", 'r')
    with fin as f:
        content = f.readlines()
    for c in content:
        str1 = c.split()
        if len(str1) == 16 and str1[8] == 'AC':
            search = True
            tolink = 'http://www.spoj.com/submit/' + str1[6] + '/id=' + str1[1]
            if Synced.objects.filter(user=username).exists():
                sync = Synced.objects.filter(user=username)
                for s in sync:
                    if s.problem == str1[6]:
                        search = False
                        break;
            if search:
                ExtractCode(tolink, str1[6], str1)


def login1(username, password):
    global userPersonalInformation, user, html, currentProblem, progress
    user = None
    html = None
    userPersonalInformation = {}
    currentProblem = None
    progress = {'numerator': 1, 'denominator': 0}
    print('Logging In...')
    s = requests.session()
    src = s.post('http://www.spoj.com/', data={"login_user": username, "password": password, "submit": "submit"})
    response = str(src.content)
    html = src.content
    if response.find('logout') == -1:
        return 0
    userPersonalInformation['username'] = username
    user = s
    return 1


def getPersonalInfo():
    global user
    response = user.get('http://www.spoj.com/manageaccount/')
    personalInfo = FetchPersonalInfo()
    personalInfo.feed(str(response.content))


def CheckUser(username, password):
    global user
    if login1(username, password) == 1:
        print('Successfully Logged In...')
        print('Syncing Problems...')
        print('Fetching User\'s Information: ')
        getPersonalInfo()
        for key in userPersonalInformation:
            print(key + ': ' + userPersonalInformation[key])
        downloadCodes(username)
        print('Fetching solved problems links...')
        return True
    else:
        print('Wrong Credentials!')
        return False


@csrf_protect
def index(request):
    global userPersonalInformation, progress
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            CheckUser(username, password)
            return redirect('profile/' + user.username)
        else:
            if CheckUser(username, password):
                user = User.objects.create_user(request.POST['username'], userPersonalInformation['email'],
                                                request.POST['password'])
                user.first_name = userPersonalInformation['first_name']
                user.last_name = userPersonalInformation['last_name']
                user.save()
                profile = Profile.objects.create(username=username, school=userPersonalInformation['school'],
                                                 img=userPersonalInformation['img'],
                                                 birthyear=userPersonalInformation['birthyear'],
                                                 city=(userPersonalInformation['city']).lower(),
                                                 solved=progress['denominator'])
                profile.save()
                login(request, user)
                return redirect('profile/' + user.username)
            else:
                return render(request, 'main/login.html', {"form": Userform(request.POST or None), "error_1": True})
    else:
        return render(request, 'main/login.html', {"form": Userform()})


def all(request):
    search_id = request.GET['search_id']
    problems = Problem.objects.filter(name__contains=search_id)
    return render(request, 'main/search.html', {"problems": problems, "search_id": search_id})


def code(request, search_id):
    path = 'main/static/solutions/' + search_id
    if not os.path.exists(path):
        raise Http404
    files = os.listdir(path)
    search_id += "/"
    return render(request, 'main/code.html', {"files": files, "search_id": search_id})


def profile(request, user_id):
    if request.user.username == user_id:
        profile = Profile.objects.get(username=user_id)
        results = Profile.objects.filter(city=profile.city).exclude(username=request.user.username)
        sync = Synced.objects.filter(user=user_id)
        return render(request, 'main/profile.html',
                      {"profile": profile, "current": False, "results": results, "list": sync})
    elif request.user.username is not None:
        user = get_object_or_404(User, username=user_id)
        profile = Profile.objects.get(username=user_id)
        results = Profile.objects.filter(city=profile.city).exclude(username=request.user.username)
        sync = Synced.objects.filter(user=user_id)
        try:
            f = Follow.objects.get(user=request.user.username, follows=user_id)
            unfollow = True
        except (Follow.DoesNotExist, Follow.MultipleObjectsReturned):
            unfollow = False
        print(unfollow)
        return render(request, 'main/profile.html',
                      {"profile": profile, "user": user, "current": True, "results": results, "list": sync,
                       "unfollow": unfollow})
    else:
        return render(request, 'main/login.html', {"form": Userform(), "error_2": True})


def logout_view(request):
    logout(request)
    return redirect('/')


def follow(request, user_id, val):
    if val == '0':
        f = Follow.objects.create(user=request.user.username)
        f.follows = user_id
        f.save()
    else:
        f = Follow.objects.get(user=request.user.username,follows=user_id)
        f.delete()
    return redirect(reverse('main:profile', kwargs={'user_id': user_id}))
