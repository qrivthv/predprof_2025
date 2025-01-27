from flask import Flask, render_template, request, redirect, url_for
from time import *
from calendar import *
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# import sqlalchemy
# from flask_login import UserMixin
import json
import _sqlite3
from sql_func import *
app = Flask(__name__)

theme = 'dark'
currentuser = {}
loggedin = False


def gn_user_check(user):
    if 128 <= ord(user['name'][0]) <= 159:
        x = ord(user['name'][0]) + 33
        user["name"] = str(chr(x)) + user['name'][1:]
    if 128 <= ord(user['name'][0]) <= 159:
        x = ord(user['surname'][0]) + 33
        user["surname"] = str(chr(x)) + user['surname'][1:]
    if 65 <= ord(user['name'][0]) <= 90:
        x = ord(user['name'][0]) - 65 + 97
        user["name"] = str(chr(x)) + user['name'][1:]
    if 65 <= ord(user['surname'][0]) <= 90:
        x = ord(user['surname'][0]) - 65 + 97
        user["surname"] = str(chr(x)) + user['surname'][1:]
    return user


@app.route('/error')
def err():
    return render_template('error.html', message="Этой страницы пока нет :(", theme=theme, loggedin=loggedin, **currentuser)


@app.route('/logout')
def logout():
    global loggedin
    global currentu
    loggedin = False
    currentu = {}
    return redirect(url_for("index"))


@app.route('/')
@app.route('/index')
def index():
    return render_template('tea.html', theme=theme, loggedin=loggedin, **currentuser)


@app.route('/my_profile', methods=['POST', 'GET'])
def myprofile():
    global loggedin
    global currentuser
    if loggedin:
        if request.method =='GET':
            x = get_my(currentuser['StudentID'])
            return render_template('myprofile.html', res=currentuser['results'], **currentuser, loggedin=loggedin, theme=theme, courses=x[0], groups=x[1], works=x[2], mycourses=x[3], mygroups=x[4], wmyorks=x[5])
        if request.method=='POST':
            x = get_my(currentuser['StudentID'])
            o = {}  # фильтрация по времени
            for key in request.form:
                if request.form[key] == '':
                    o[key] = 0
                else:
                    o[key] = int(request.form[key])
            timer = 60 * o['min'] + 3600 * o['hour'] + 86400 * o['day'] + 2629743 * o['month'] + 31556926 * o['year']
            return render_template('myprofile.html', res=get_user_result(currentuser['StudentID'], timer), **currentuser, loggedin=loggedin, theme=theme, courses=x[0], groups=x[1], works=x[2], mycourses=x[3], mygroups=x[4], wmyorks=x[5])
    else:
        return redirect(url_for("login"))


@app.route('/profile')
def profile(username):
    # s = f"select * from Users where username = '{username}'"
    x = get_user(username)
    return render_template('profile.html',res=x['results'], user=x, **currentuser, loggedin=loggedin, theme=theme)


@app.route('/login', methods=['POST', 'GET'])
def login():
    global loggedin
    global currentuser
    if loggedin:
        return redirect('myprofile')
    if request.method == 'GET':
        return render_template('login.html', message=' ',theme=theme, **currentuser, loggedin=loggedin)
    elif request.method == 'POST':
        ss = 'EmailOrUname'
        s = request.form[ss].strip()
        u = get_user(s, s)
        cu = currentuser
        if u != 'No such user':
            if u != ():
                if u['password'] == request.form["password"].strip():
                    currentuser = u
                    loggedin = True
                    return  redirect(url_for("myprofile"))
        return render_template('login.html', message="Неверный логил или пароль", theme=theme, **currentuser, loggedin=loggedin)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        if loggedin:
            return redirect('my_profile')
        return render_template("register.html", s="Зарегистрироваться", loggedin=loggedin, message='', theme=theme, **currentuser)
    elif request.method == 'POST':
        new_user = {}
        for k in request.form:
            new_user[k] = request.form[k].strip()
        new_user["password"] = request.form['password'].strip()
        new_user["passwordcheck"] = request.form['passwordcheck'].strip()
        if new_user["passwordcheck"] != new_user["password"]:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, пароли не совпадают", theme=theme, **currentuser)
        new_user = gn_user_check(new_user)
        email = str(new_user["email"]).replace('@', '?')
        r = int(new_user["colour"][1:3], 16)
        g = int(new_user["colour"][3:5], 16)
        b = int(new_user["colour"][5:7], 16)
        if r > 150 or b>150 or g > 150:
            new_user["bright"] = True
        else:
            new_user["bright"] = False
        s1 = f'select email, username, phone from Users where email = "{email}"'
        s2 = f'select email, username, phone from Users where username = "{new_user["username"]}"'
        s3 = f'select email, username, phone from Users where phone="{new_user["phone"]}"'
        x1 = get_data(s1)
        x2 = get_data(s2)
        x3 = get_data(s3)
        if len(x2) != 0:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, этот никнейм уже занят", theme=theme)
        if len(x1) != 0:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, эта почта уже зарегестрирована", theme=theme)
        if len(x3) != 0:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, этот номер телефона уже зарегестрирован", theme=theme)
        #  genius user check
        s = f'''
        insert into Users (username, email, phone, password, SName, SSurname,  Grade, avgresults, color, bright, adm) 
        values 
        (?, ?, ?, ?, ?, ?,  ?, ?, ?, ?)
        '''
        rr = "0!0$"*27
        a = (new_user["username"], email, int(new_user["phone"]), new_user["password"], new_user["name"], new_user["surname"], int(new_user["grade"]), rr, new_user["colour"], new_user["bright"], 0)
        insrt(a, s)
        return redirect('login')


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    return render_template('error.html', message='Этой страницы пока нет', loggedin=loggedin, **currentuser)
    # global currentu
    # if request.method == "GET":
    #     return render_template('register.html', s="Редактировать", auth=loggedin, **currentu, message='')
    # elif request.method == "POST":
    #     for i in range(len(data)):
    #         user = data[i]
    #         if user["username"] == currentu["username"]:
    #             in_db1 = True
    #             n_u = currentu
    #             for k in request.form:
    #                 if k == 'username' and n_u['username'] != request.form[k]:
    #                     for user in data:
    #                         if user["username"] == request.form["username"].strip():
    #                             in_db1 = True
    #                             break
    #                     if in_db1:
    #                         return render_template('register.html', s="Редактировать", auth=loggedin,
    #                                                message="К сожалению этот никнейм уже занят")
    #                     else:
    #                         n_u[k] = request.form[k]
    #                     continue
    #                 if k == 'email' and n_u['email'] != request.form[k]:
    #                     for user in data:
    #                         if user["email"] == request.form["email"].strip():
    #                             in_db1 = True
    #                             break
    #                     if in_db1:
    #                         return render_template('register.html', s="Редактировать", auth=loggedin,
    #                                                message="К сожалению, эта почта уже занята")
    #                     else:
    #                         n_u[k] = request.form[k]
    #                     continue
    #                 if request.form[k] != "":
    #                     n_u[k] = request.form[k]
    #
    #             # genius user check
    #             n_u = gn_user_check(n_u)
    #             currentu = n_u
    #             data[i] = n_u
    #             with open("users.json", "w", encoding='utf-8') as file:
    #                 json.dump(data, file, indent=2, ensure_ascii=False)
    #             return logout()


# @app.route('/results')
# def res(results, show):
#     return render_template('results.html', tasks=tasks, res=results, show=show, theme=theme)


@app.route('/test/<int:num>', methods=['POST', 'GET'])
def test(num):
    s = f'select * from Problem where Type = {num}'
    x = get_data(s)
    o = len(x)
    if request.method == 'GET':
        return render_template('test.html', tasks=x, theme=theme, loggedin=loggedin, currentuser=currentuser)
    if request.method == 'POST':
        cur_time = timegm(gmtime())
        results = []
        rcount = 0
        for i in range(o):
            results.append([0, 0, 0])
        for i in range(o):
            name = f'{x[i][0]}'
            if loggedin:
                s = 'insert into WorkResult (ProblemID, WorkID, GroupID, StudentID, date, result) values (?, ?, ?, ?, ?, ?)'
                res = [int(name), 0, 0, currentuser['StudentID'], cur_time]
                if request.form[name].strip() != '':
                    ans = int(request.form[name].strip())
                    results[i][1] = ans
                    results[i][0] = i
                    if ans == int(x[i][2]):
                        results[i][2] = 1
                        res.append(1)
                        rcount += 1
                    else:
                        results[i][2] = 0
                        res.append(0)
                else:
                    res.append(0)
                    results[i][0] = i
                    results[i][1] = ""
                    results[i][2] = 0
                insrt(res, s)
                currentuser['results'] = get_user_result(currentuser['StudentID'])
            else:
                if request.form[name].strip() != '':
                    ans = int(request.form[name].strip())
                    results[i][1] = ans
                    results[i][0] = i
                    if ans == int(x[i][2]):
                        results[i][2] = 1
                        rcount += 1
                    else:
                        results[i][2] = 0
                else:
                    results[i][0] = i
                    results[i][1] = ""
                    results[i][2] = 0
        show = str(request.form.get("show")) != "None"
        return render_template('results.html', tasks=x, res=results,  showAns=show, showScore=show, right=rcount, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/work/<int:workid>/<int:groupid>', methods=['POST', 'GET'])
def work(workid, groupid):
    if not loggedin:
        return redirect(url_for('login'))
    s = f'select ShowAns, ShowScore from WorkGroup where WorkID={workid} and GroupID={groupid}'
    dt = get_data(s)
    dt = dt[0]
    s = f'''select Problem.ProblemID, Statement, Answer, Type, Creator, Solution, code, Diff, file, filename, img1, img2
        from Problem join WorkProblem on Problem.ProblemID = WorkProblem.ProblemID where WorkID = {workid}'''
    tasks = get_data(s)
    o = len(tasks)
    if request.method == "GET":
        return render_template('test.html', tasks=tasks, theme=theme, loggedin=loggedin, currentuser=currentuser)
    elif request.method == 'POST':
        cur_time = timegm(gmtime())
        results = []
        rcount = 0
        for i in range(o):
            results.append([0, 0, 0])
        for i in range(o):
            name = f'{tasks[i][0]}'
            s = 'insert into WorkResult (ProblemID, WorkID, GroupID, date, result) values (?, ?, ?, ?, ?)'
            res = [int(name), workid, groupid, cur_time]
            if request.form[name].strip() != '':
                ans = int(request.form[name].strip())
                results[i][1] = ans
                results[i][0] = i
                if ans == int(tasks[i][2]):
                    results[i][2] = 1
                    res.append(1)
                    rcount += 1
                else:
                    results[i][2] = 0
                    res.append(0)
            else:
                res.append(0)
                results[i][0] = i
                results[i][1] = ""
                results[i][2] = 0
            insrt(res, s)
            currentuser['results'] = get_user_result(currentuser['StudentID'])
            return render_template('results.html', tasks=tasks, res=results, showAns=dt[0], showScore=dt[1], right=rcount, theme=theme,
                               **currentuser, loggedin=loggedin)


@app.route('/train/<int:num>', methods=['POST', 'GET'])
def train(num):
    s = f'select * from Problem where Type = {num}'
    x = get_data(s)
    o = len(x)
    ans = []
    for task in x:
        ans.append(task[2])
    return render_template('train.html', tasks=x, answers=ans, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'GET':
        return render_template('add.html', theme=theme, **currentuser, loggedin=loggedin)
    if request.method == 'POST':
        statement = request.form['stat']
        answer = request.form['ans']
        solution = request.form['sol'].replace('\n', '<br>')
        diff = request.form['diff']
        typ = int(request.form['type'])
        creator = request.form['author']
        filename = request.files['file'].filename
        file = request.files['file']
        img1name = request.files['img1'].filename
        img1 = request.files['img1']
        img2name = request.files['img2'].filename
        img2 = request.files['img2']

        s = f'select * from Problem where Statement="{statement}"'
        a = get_data(s)
        if diff == 'base':
            diff = 1
        elif diff == 'ke':
            diff = 3
        else:
            diff = 2
        if a != []:
            return render_template('add.html', theme=theme, **currentuser, loggedin=loggedin, message='Задача с таким условием уже есть :(')
        if filename != '':
            if_file = 1
        else:
            if_file = 0
        if img1name != '':
            if_img1 = 1
        else:
            if_img1 = 0
        if img2name != '':
            if_img2 = 1
        else:
            if_img2 = 0
        s = f'insert into Problem (Statement, Answer, Type, Creator, Solution, Diff, file) values (?, ?, ?, ?, ?, ?, ?)'
        a = [statement, answer, typ, creator, solution, diff, if_file]
        insrt(a, s)
        if if_file:
            s = f'select ProblemID from Problem where Statement="{statement}"'
            a = get_data(s)
            while type(a) is not int:
                a = a[0]
            typee = filename.split('.')[1]
            path = 'static/files/problem' + str(a) + str(typee)
            file.save(path)
            s = f'update Problem set filename="{path[7:]}" where ProblemID={a}'
            upd(s)
        if if_img1:
            s = f'select ProblemID from Problem where Statement="{statement}"'
            a = get_data(s)
            while type(a) is not int:
                a = a[0]
            typee = img1name.split('.')[1]
            path = 'static/files/img1' + str(a) + '.' + str(typee)
            img1.save(path)
            s = f'update Problem set img1="{path[7:]}" where ProblemID={a}'
            upd(s)
        if if_img2:
            s = f'select ProblemID from Problem where Statement="{statement}"'
            a = get_data(s)
            while type(a) is not int:
                a = a[0]
            typee = img2name.split('.')[1]
            path = 'static/files/img2' + str(a) + '.' + str(typee)
            img2.save(path)
            s = f'update Problem set img2="{path[7:]}" where ProblemID={a}'
            upd(s)
        return redirect(url_for('bank'))


@app.route('/settings', methods=['POST', 'GET'])
def settings():
    global theme
    if request.method == 'GET':
        return render_template('settings.html', theme=theme, **currentuser, loggedin=loggedin)
    if request.method == 'POST':
        theme = request.form['changetheme']
        return redirect(url_for('index'))


@app.route('/courses')
def courses():
    s = f"select * from Courses"
    a = get_data(s)
    return render_template('courses.html', courses=a, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/forum', methods=['POST', 'GET'])
def forum():
    s = f"select * from Questions order by date desc"
    a = get_data(s)
    b = []
    tm = timegm(gmtime())
    if request.method == 'GET':
        for i in a:
            k = list(i)
            dd = i[3]
            ss = gmtime(dd)
            ss = asctime(ss)
            ss = str(ss)
            k[3] = ss[4:16] + ss[19:]
            if dd + 1737647353 >= tm and dd <= tm:
                b.append(k)
        return render_template('forum.html', category="Недавние", questions=b, theme=theme, **currentuser, loggedin=loggedin)
    elif request.method == 'POST':
        tm = timegm(gmtime())
        b =[]
        for i in a:
            o = {} #фильтрация по времени
            for key in request.form:
                if key != 'txt':
                    if request.form[key] == '':
                        o[key] = 0
                    else:
                        o[key] = int(request.form[key])
            txt = request.form['txt']
            delta = 60*o['min'] + 3600*o['hour'] + 86400 * o['day'] + 2629743 * o['month'] + 31556926 * o['year']
            if delta == 0:
                delta = 1737647353
            k = list(i)
            dd = i[3]
            ss = gmtime(dd)
            ss = asctime(ss)
            ss = str(ss)
            k[3] = ss[4:16] + ss[19:]
            if dd + delta >= tm and dd <= tm and txt != '' and txt in i[2]:
                b.append(k)
        return render_template('forum.html', category="Выбранные", questions=b, theme=theme, **o, **currentuser, loggedin=loggedin, txt=txt)
    return render_template('forum.html', category="Недавние", questions=b, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/question/<int:qid>', methods=['POST', 'GET'])
def ans(qid):
    s1 = f'select * from Questions where QID = {qid}'
    x1 = get_data(s1)
    if request.method == 'POST':
        user = request.form['username']
        tm = timegm(gmtime())
        text = request.form['answer']
        s = f'insert into Answers (QID, Author, Statement, date) values (?, ?, ?, ?)'
        a = [qid, user, text, tm]
        insrt(a, s)
    s2 = f'select * from Answers where QID = {qid} order by date desc'
    x2 = get_data(s2)
    q = list(x1[0])
    dd = x1[0][3]
    ss = gmtime(dd)
    ss = asctime(ss)
    ss = str(ss)
    q[3] = ss[4:16] + ss[19:]
    return render_template('question.html', answers=x2, question=q, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/course/<int:id>/<int:num>')
def course(id, num):
    s = f'select Courses.CID, CName, Type, Link, text, lang, code from CourseMaterial join Courses on Courses.CID = CourseMaterial.CID where Courses.CID = {id} and Type={num}'
    a = get_data(s)
    if len(a) == 1:
        a = a[0]
    return render_template('course.html', course=a, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/ask', methods=['POST', 'GET'])
def ask():
    if request.method == 'GET':
        return render_template('ask.html', theme=theme, **currentuser, loggedin=loggedin)
    if request.method == 'POST':
        question = request.form['q']
        user = request.form['username']
        if user == '':
            user = 'неизвестный'
        tm = timegm(gmtime())
        s = f'insert into Questions (Author, Statement, date, Open) values (?, ?, ?, ?)'
        a = [user, question, tm, 1]
        insrt(a, s)
        s = f'select QID from Questions where date = {tm}'
        x = get_data(s)
        x = x[0]
        return render_template('tea.html', theme=theme, **currentuser, loggedin=loggedin)
    return render_template('ask.html', theme=theme, **currentuser, loggedin=loggedin)


@app.route('/bank', methods=['POST', 'GET'])
def bank():
    s = f"select * from Problem order by ProblemID desc, Diff "
    a = get_data(s)
    b = []
    tm = timegm(gmtime())
    if request.method == 'GET':
        for i in a:
            k = list(i)
            b.append(k)
        return render_template('bank.html', category="Все", tasks=b, theme=theme, **currentuser, loggedin=loggedin)
    elif request.method == 'POST':
        b = []
        for i in a:
            k = list(i)
            kim = request.form['kim']
            diff = request.form['diff']
            txt = request.form['txt']
            if (len(kim) != 0 and k[3] == int(kim)) or len(kim) == 0:
                if (len(diff) != 0 and k[7] == int(diff)) or len(diff) == 0:
                    if (len(txt) != 0 and txt in k[1]) or len(txt) == 0:
                        b.append(k)
        return render_template('bank.html', category="Выбранные", tasks=b, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/add_group', methods=['POST', 'GET'])
def add_group():
    if not loggedin:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('add_group.html', theme=theme, **currentuser, loggedin=loggedin)
    if request.method == 'POST':
        name = request.form['name']
        students = request.form['stud'].split()
        teachers = request.form['teach'].split()
        s = f'select GroupID from Groups where GroupName = "{name}"'
        a = get_data(s)
        if a !=[]:
            return render_template('add_group.html', message='Группа с таким названием уже есть', theme=theme, **currentuser, loggedin=loggedin)
        s = f'insert into Groups (GroupName) values (?)'
        a = [name]
        insrt(a, s)
        s = f'select GroupID from Groups where GroupName = "{name}"'
        a = get_data(s)
        a = a[0]
        if type(a) is not int:
            id = a[0]
        else:
            id = a
        s = f'insert into GroupTeacher (GroupID, CreatorID) values (?, ?)'
        a = [id, currentuser['StudentID']]
        insrt(a, s)
        if teachers != []:
            for user in teachers:
                if ',' in user:
                    user = user.replace(',', '')
                s = f'select StudentID from Users where username="{user}"'
                a = get_data(s)
                a = a[0]
                if type(a) is not int:
                    id1 = a[0]
                else:
                    id1 = a
                s = f'insert into GroupTeacher (GroupID, CreatorID) values (?, ?)'
                a = [id, id1]
                insrt(a, s)
        for user in students:
            if ',' in user:
                user = user.replace(',', '')
            s = f'select StudentID from Users where username="{user}"'
            a = get_data(s)
            a = a[0]
            if type(a) is not int:
                id1 = a[0]
            else:
                id1 = a
            s = f'insert into GroupStud (GroupID, StudID) values (?, ?)'
            a = [id, id1]
            insrt(a, s)
        return render_template('tea.html', theme=theme, loggedin=loggedin, **currentuser)


@app.route('/dashboard/<int:id>')
def dashboard(id):
    if not loggedin:
        return redirect(url_for('login'))
    s = f'select GroupName from Groups where GroupID = {id}'
    a = get_data(s)
    a = a[0]
    if type(a) is not str:
        GName = a[0]
    else:
        GName = a
    s = f'select SName, SSurname, username from GroupTeacher join Users on GroupTeacher.CreatorID = Users.StudentID where GroupID = {id}'
    teachers = get_data(s)
    teacher = False
    for i in teachers:
        if currentuser['username'] in i:
            teacher = True
            break
    s = f'select SName, SSurname, username from GroupStud join Users on GroupStud.StudID = Users.StudentID where GroupID = {id}'
    students = get_data(s)
    s = f'select Work.WorkID, CreatorID, WorkName from WorkGroup join Work on WorkGroup.WorkID = Work.WorkID where GroupID = {id}'
    works = get_data(s)
    return render_template('dashboard.html', theme=theme, loggedin=loggedin, **currentuser, GName=GName, teachers=teachers, students=students, works=works, id=id, teacher=teacher)


@app.route('/addTest', methods=['POST', 'GET'])
def addTest():
    if request.method == 'GET':
        return render_template('addTest.html', theme=theme, **currentuser, loggedin=loggedin)
    if request.method == 'POST':
        typ = int(request.form['type'])
        creator = request.form['author']
        answer = request.form['ans']
        sA = f"select * from Users order by StudentID "
        aA = get_data(sA)
        id = 0
        for i in aA:
            if i[1] == creator:
                id = i[0]
                break

        s = f'insert into Work (CreatorID, WorkName) values (?, ?)'
        a = [id, answer]
        insrt(a, s)

        sW = f'select * from Work order by CreatorID'
        aW = get_data(sW)
        wID = 0

        for i in aW:
            if i[1] == id and i[2] == answer:
                wID = i[0]
        pr = request.form['stat']
        x = pr.split()
        arr = []
        for i in x:
            arr.append(int(i))
        for i in arr:
            s1 = f'insert into WorkProblem (WorkID, ProblemID) values (?, ?)'
            a1 = [wID, i]
            insrt(a1, s1)

        return render_template('tea.html', theme=theme, **currentuser, loggedin=loggedin)


@app.route('/add_gr/<int:id>', methods=['POST', 'GET'])
def add1(id):
    if request.method == 'GET':
        return render_template('add_group.html', theme=theme, **currentuser, loggedin=loggedin)
    if request.method == 'POST':
        students = request.form['stud'].split()
        teachers = request.form['teach'].split()
        if teachers != []:
            for user in teachers:
                if ',' in user:
                    user = user.replace(',', '')
                s = f'select StudentID from Users where username="{user}"'
                a = get_data(s)
                a = a[0]
                if type(a) is not int:
                    id1 = a[0]
                else:
                    id1 = a
                s = f'select GroupID, CreatorID from GroupTeacher where CreatorID={id1} and GroupID={id}'
                a = get_data(s)
                if a == []:
                    s = f'insert into GroupTeacher (GroupID, CreatorID) values (?, ?)'
                    a = [id, id1]
                    insrt(a, s)
        for user in students:
            if ',' in user:
                user = user.replace(',', '')
            s = f'select StudentID from Users where username="{user}"'
            a = get_data(s)
            a = a[0]
            if type(a) is not int:
                id1 = a[0]
            else:
                id1 = a
            s = f'select GroupID, StudID from GroupStud where StudID={id1} and GroupID={id}'
            a = get_data(s)
            if a == []:
                s = f'insert into GroupStud (GroupID, StudID) values (?, ?)'
                a = [id, id1]
                insrt(a, s)
        return redirect(url_for('dashboard', id=id))


@app.route('/work_results/<int:workid>/<int:groupid>')
def work_result(workid, groupid):
    s = f'select distinct CreatorID from GroupTeacher where GroupID={groupid}'
    a = get_data(s)
    teachers = []
    for i in a:
        teachers.append(i[0])
    if loggedin and currentuser['StudentID'] in teachers:
        results = get_group_result_work(groupid, workid)
        s = f'select WorkName from Work where WorkID = {workid}'
        a = get_data(s)
        while type(a) is not str:
            a = a[0]
        work_name = a
        s = f'select GroupName from Groups where GroupID = {groupid}'
        a = get_data(s)
        while type(a) is not str:
            a = a[0]
        group_name = a
        return render_template('work_results.html',  theme=theme, **currentuser, loggedin=loggedin, group_name=group_name, work_name=work_name, work_results=results)
    else:
        #return redirect(url_for('restricted'))
        return redirect(url_for('error'))



if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
