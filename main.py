from flask import Flask, render_template, request, redirect, url_for
from time import *
from calendar import *
# from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# import sqlalchemy
# from flask_login import UserMixin
import json
import _sqlite3

app = Flask(__name__)

theme = 'dark'


def get_data(what):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(what)
    line = curs.fetchall()
    c.commit()
    c.close()
    return line


def insrt(data, what):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(what, data)
    line = curs.fetchall()
    c.commit()
    c.close()
    return


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
    return render_template('error.html', message="Этой страницы пока нет :(", theme=theme)


@app.route('/logout')
def logout():
    global loggedin
    global currentu
    loggedin = False
    currentu = {}
    return index()


@app.route('/')
@app.route('/index')
def index():
    return render_template('tea.html', theme=theme)


@app.route('/myprofile/<username>')
def myprofile(x):
    if loggedin:
        print(x)
        user = {
            "username": x[1],
            "email": x[2].replace('?', '@'),
            "phone": x[3],
            "name": x[5],
            "surname": x[6],
            "grade": x[7],
            "color": x[9],
            "bright": x[10]
        }
        r = []
        k = 0
        n = 0
        for i in x[8]:
            if i == "$":
                r.append([n, k])
                k = 0
            elif i == '!':
                n = k
                k = 0
            else:
                k *= 10
                k += int(i)
        return render_template('myprofile.html', res=r, **user, auth=loggedin, theme=theme)
    else:
        return login()


@app.route('/my_profile')
#@app.route('/myprofile')
def profile(user):
    # s = f"select * from Student where username = '{username}'"
    x = user
    if len(x) != 0:
        user = {
            "username": x[1],
            "email": x[2],
            "phone": x[3],
            "name": x[5],
            "surname": x[6],
            "grade": x[7],
            "color": x[9],
            "bright": x[10]
        }
        r =[]
        k = 0
        n = 0
        for i in x[8]:
            if i == "$":
                r.append([n, k])
                k = 0
            if i == '!':
                n = k
                k = 0
            else:
                k *= 10
                k += int(i)
        return render_template('profile.html',res=r, **user, auth=loggedin, theme=theme)
    return err()


@app.route('/login', methods=['POST', 'GET'])
def login():
    global loggedin
    if loggedin:
        return redirect('/myprofile')
    if request.method == 'GET':
        return render_template('login.html', message=' ',theme=theme)
    elif request.method == 'POST':
        s = f"select * from Student where username = '{request.form['EmailOrUname'].strip()}' or email = '{request.form['EmailOrUname'].strip()}'"
        u = get_data(s)
        if len(u[0]) > 1:
            u = u[0]
        if u != ():
            print(u)
            if u[4] == request.form["password"].strip():
                global currentu
                loggedin = True
                currentu = u
                return myprofile(u)
        return render_template('login.html', message="Неверный логил или пароль", theme=theme)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        if loggedin:
            return redirect('/my_profile')
        return render_template("register.html", s="Зарегистрироваться", auth=loggedin, message='', theme=theme)
    elif request.method == 'POST':
        new_user = {}
        for k in request.form:
            new_user[k] = request.form[k].strip()
            print(k, request.form[k].strip())
        new_user["password"] = request.form['password'].strip()
        new_user["passwordcheck"] = request.form['passwordcheck'].strip()
        if new_user["passwordcheck"] != new_user["password"]:
            return render_template('register.html', s="Зарегистрироваться", auth=loggedin, message="К сожалению, пароли не совпадают", theme=theme)
        new_user = gn_user_check(new_user)
        email = str(new_user["email"]).replace('@', '?')
        print(email)
        r = int(new_user["colour"][1:3], 16)
        g = int(new_user["colour"][3:5], 16)
        b = int(new_user["colour"][5:7], 16)
        if r > 150 or b>150 or g > 150:
            new_user["bright"] = True
        else:
            new_user["bright"] = False
        s1 = f'select email, username, phone from Student where email = "{email}"'
        s2 = f'select email, username, phone from Student where username = "{new_user["username"]}"'
        s3 = f'select email, username, phone from Student where phone="{new_user["phone"]}"'
        x1 = get_data(s1)
        x2 = get_data(s2)
        x3 = get_data(s3)
        if len(x2) != 0:
            return render_template('register.html', s="Зарегистрироваться", auth=loggedin, message="К сожалению, этот никнейм уже занят", theme=theme)
        if len(x1) != 0:
            return render_template('register.html', s="Зарегистрироваться", auth=loggedin, message="К сожалению, эта почта уже зарегестрирована", theme=theme)
        if len(x3) != 0:
            return render_template('register.html', s="Зарегистрироваться", auth=loggedin, message="К сожалению, этот номер телефона уже зарегестрирован", theme=theme)
        #  genius user check

        s = f'''
        insert into Student (username, email, phone, password, SName, SSurname,  Grade, avgresults, color, bright) 
        values 
        (?, ?, ?, ?, ?, ?,  ?, ?, ?, ?)
        '''
        rr = "0!0$"*27
        a = (new_user["username"], email, int(new_user["phone"]), new_user["password"], new_user["name"], new_user["surname"], int(new_user["grade"]), rr, new_user["colour"], new_user["bright"])
        insrt(a, s)
        return redirect('/login')


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    return render_template('error.html', message='Этой страницы пока нет')
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


@app.route('/results')
def res(results, show):
    return render_template('results.html', tasks=tasks, res=results, show=show, theme=theme)


@app.route('/test/<int:num>', methods=['POST', 'GET'])
def test(num):
    s = f'select * from Problem where Type = {num}'
    x = get_data(s)
    o = len(x)
    if request.method == 'GET':
        return render_template('test.html', tasks=x, theme=theme)
    if request.method == 'POST':
        results = []
        rcount = 0
        for i in range(o):
            results.append([0, 0, 0])
        for i in range(o):
            name = f'{x[i][0]}'
            if request.form[name].strip() != '':
                ans = int(request.form[name].strip())
                results[i][1] = ans
                results[i][0] = i
                if ans == int(x[i][2]):
                    results[i][2] = "right"
                    rcount += 1
                else:
                    results[i][2] = "wrong"
            else:
                results[i][0] = i
                results[i][1] = ""
                results[i][2] = "wrong"
        show = str(request.form.get("show")) != "None"
        print(results, show)
        return render_template('results.html', tasks=x, res=results, show=show, right=rcount, theme=theme)


@app.route('/train/<int:num>', methods=['POST', 'GET'])
def train(num):
    s = f'select * from Problem where Type = {num}'
    x = get_data(s)
    o = len(x)
    ans = []
    for task in x:
        ans.append(task[2])
    return render_template('train.html', tasks=x, answers=ans, theme=theme)


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'GET':
        return render_template('add.html', theme=theme)
    if request.method == 'POST':
        statement = request.form['stat']
        answer = request.form['ans']
        solution = request.form['sol'].replace('\n', '<br>')
        diff = request.form['diff']
        typ = int(request.form['type'])
        creator = request.form['author']
        s = f'insert into Problem (Statement, Answer, Type, Creator, Solution, Diff) values (?, ?, ?, ?, ?, ?)'
        a = [statement, answer, typ, creator, solution, diff]
        print(a)
        insrt(a, s)
        return render_template('tea.html', theme=theme)


@app.route('/settings', methods=['POST', 'GET'])
def settings():
    global theme
    if request.method == 'GET':
        return render_template('settings.html', theme=theme)
    if request.method == 'POST':
        theme = request.form['changetheme']
        return render_template('tea.html', theme=theme)


@app.route('/courses')
def courses():
    s = f"select * from Courses"
    a = get_data(s)
    return render_template('courses.html', courses=a, theme=theme)


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
        return render_template('forum.html', category="Недавние", questions=b, theme=theme)
    elif request.method == 'POST':
        tm = timegm(gmtime())
        b =[]
        for i in a:
            o = {}
            for key in request.form:
                if key != 'txt':
                    if request.form[key] == '':
                        o[key] = 0
                    else:
                        o[key] = int(request.form[key])
            delta = 60*o['min'] + 3600*o['hour'] + 86400 * o['day'] + 2629743 * o['month'] + 31556926 * o['year']
            if delta == 0:
                delta = 1737647353
            k = list(i)
            dd = i[3]
            ss = gmtime(dd)
            ss = asctime(ss)
            ss = str(ss)
            k[3] = ss[4:16] + ss[19:]
            if dd + delta >= tm and dd <= tm:
                b.append(k)
        return render_template('forum.html', category="Выбранные", questions=b, theme=theme, **o)
    return render_template('forum.html', category="Недавние", questions=b, theme=theme)


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
        print(a)
        insrt(a, s)
    s2 = f'select * from Answers where QID = {qid} order by date desc'
    x2 = get_data(s2)
    q = list(x1[0])
    dd = x1[0][3]
    ss = gmtime(dd)
    ss = asctime(ss)
    ss = str(ss)
    q[3] = ss[4:16] + ss[19:]
    return render_template('question.html', answers=x2, question=q, theme=theme)


@app.route('/course/<int:id>/<int:num>')
def course(id, num):
    s = f'select Courses.CID, CName, Type, Link from CourseMaterial join Courses on Courses.CID = CourseMaterial.CID where Courses.CID = {id} and Type={num}'
    a = get_data(s)
    if len(a) == 1:
        a = a[0]
    return render_template('course.html', course=a, theme=theme)


@app.route('/ask', methods=['POST', 'GET'])
def ask():
    if request.method == 'GET':
        return render_template('ask.html', theme=theme)
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
        print(user, question, tm)
        return render_template('tea.html', theme=theme)
    return render_template('ask.html', theme=theme)

loggedin = False
currentu = {}
if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
