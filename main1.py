from flask import Flask, render_template, request, redirect, url_for, flash
from time import *
from calendar import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
# import sqlalchemy
from flask_login import UserMixin
import json
import _sqlite3
from sql_func1 import *
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
theme = 'dark'
currentuser = {}
loggedin = False
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(user_data)
    return None


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data[0]
        self.username = user_data[1]
        self.password = user_data[4]
        self.name = user_data[5]
        self.surname = user_data[6]
        self.email = user_data[2].replace('?', '@')
        self.phone = user_data[3]
        self.grade = user_data[7]
        self.color = user_data[8]
        self.bright = user_data[9]
        self.adm = user_data[10]
        self.results = user_data[11]


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


@app.errorhandler(404)
@app.errorhandler(400)
@app.errorhandler(500)
def smth_happened(error):
    return redirect(url_for('err'))


@app.route('/error')
def err():
    return render_template('error.html', message="Что-то пошло не так<br>Вероятно, этой страницы пока нет :(", theme=theme, loggedin=loggedin, **currentuser)


@app.errorhandler(401)
def unauthorized():
    if loggedin:
        redirect(url_for('logout'))
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
def index():
    s = 'select * from Courses where CID = ? or CID = ? or CID == ?'
    favcourses = get_data(s, [1, 9, 8])
    return render_template('tea.html', theme=theme, loggedin=loggedin, **currentuser, favcourses=favcourses)


@app.route('/my_profile', methods=['POST', 'GET'])
@login_required
def myprofile():
    if request.method == 'GET':
        x = get_my(current_user.id)
        return render_template('myprofile.html', res=current_user.results, **current_user.__dict__, loggedin=loggedin, theme=theme, courses=x[0], groups=x[1], works=x[2], mycourses=x[3], mygroups=x[4], wmyorks=x[5])
    if request.method == 'POST':
        x = get_my(current_user.id)
        o = {}  # фильтрация по времени
        for key in request.form:
            if request.form[key] == '':
                o[key] = 0
            else:
                o[key] = int(request.form[key])
        timer = 60 * o['min'] + 3600 * o['hour'] + 86400 * o['day'] + 2629743 * o['month'] + 31556926 * o['year']
        return render_template('myprofile.html', res=get_user_result(current_user.id, timer), **current_user.__dict__, loggedin=loggedin, theme=theme, courses=x[0], groups=x[1], works=x[2], mycourses=x[3], mygroups=x[4], wmyorks=x[5])


@app.route('/profile')
def profile(username):
    x = get_user(username)
    return render_template('profile.html',res=x['results'], user=x, **currentuser, loggedin=loggedin, theme=theme)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('myprofile'))

    if request.method == 'GET':
        return render_template('login.html', message=' ', theme=theme, loggedin=loggedin)

    elif request.method == 'POST':
        ss = 'EmailOrUname'
        s = request.form[ss].strip()
        u = get_user(s, s)
        if u != 'No such user' and u != ():
            if u['password'] == request.form["password"].strip():
                u = get_user_by_id(u['StudentID'])
                user = User(u)
                login_user(user)
                return redirect(url_for("myprofile"))

        return render_template('login.html', message="Неверный логин или пароль", theme=theme, loggedin=loggedin)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('my_profile'))
        return render_template("register.html", s="Зарегистрироваться", loggedin=loggedin, message='', theme=theme)
    elif request.method == 'POST':
        new_user = {}
        important = ['name', 'surname', 'username', 'email', 'password']
        for k in request.form:
            if k in important and request.form[k] == "":
                return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin,
                                       message="К сожалению, вы не заполнили жизненно важные поля", theme=theme)

            new_user[k] = request.form[k].strip()
        new_user["password"] = request.form['password'].strip()
        new_user["passwordcheck"] = request.form['passwordcheck'].strip()
        if new_user["passwordcheck"] != new_user["password"]:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, пароли не совпадают", theme=theme)
        new_user = gn_user_check(new_user)
        email = str(new_user["email"]).replace('@', '?')
        r = int(new_user["colour"][1:3], 16)
        g = int(new_user["colour"][3:5], 16)
        b = int(new_user["colour"][5:7], 16)
        if r > 150 or b>150 or g > 150:
            new_user["bright"] = True
        else:
            new_user["bright"] = False
        s1 = 'select email, username, phone from Users where email = ?'
        s2 = 'select email, username, phone from Users where username = ?'
        s3 = 'select email, username, phone from Users where phone=?'
        x1 = get_data(s1, [email])
        x2 = get_data(s2, [new_user["username"]])
        x3 = get_data(s3, [new_user['phone']])
        if len(x2) != 0:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, этот никнейм уже занят", theme=theme)
        if len(x1) != 0:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, эта почта уже зарегестрирована", theme=theme)
        if len(x3) != 0:
            return render_template('register.html', s="Зарегистрироваться", loggedin=loggedin, message="К сожалению, этот номер телефона уже зарегестрирован", theme=theme)
        #  genius user check
        s = '''
        insert into Users (username, email, phone, password, SName, SSurname,  Grade, color, bright, adm) 
        values 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        rr = "0!0$"*27
        a = (new_user["username"], email, int(new_user["phone"]), new_user["password"], new_user["name"], new_user["surname"], int(new_user["grade"]), new_user["colour"], new_user["bright"], 0)
        insrt(a, s)
        return redirect(url_for('login'))


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    if request.method == 'GET':
        # Отображаем форму редактирования с текущими данными пользователя
        return render_template('register.html', s="Редактировать", message='', theme=theme)

    elif request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip().replace('@', '?')
        new_phone = int(request.form.get('phone', '').strip())
        new_name = request.form.get('name', '').strip()
        new_surname = request.form.get('surname', '').strip()
        new_color = request.form.get('colour', '').strip()
        bright = current_user.bright
        new_grade = int(request.form.get('grade', ''))
        r = int(str(new_color)[1:3], 16)
        g = int(str(new_color)[3:5], 16)
        b = int(str(new_color)[5:7], 16)
        if r > 150 or b > 150 or g > 150:
            bright = True
        # Проверка, что новый username не занят другим пользователем
        if new_username != current_user.username:
            s = 'SELECT username FROM Users WHERE username = ?'
            existing_user = get_data(s, [new_username])
            if existing_user:
                flash("К сожалению, этот никнейм уже занят.", "error")
                return render_template('register.html', user=current_user, s='Редактировать',
                                       message="К сожалению, этот никнейм уже занят", theme=theme)

        # Проверка, что новый email не занят другим пользователем
        if new_email.replace('?', '@') != current_user.email:
            s = 'SELECT email FROM Users WHERE email = ?'
            existing_email = get_data(s, [new_email])
            if existing_email:
                flash("К сожалению, эта почта уже занята.", "error")
                return render_template('register.html', user=current_user,
                                       message="К сожалению, эта почта уже занята", theme=theme)

        # Обновление данных пользователя в базе данных
        s = '''
                UPDATE Users 
                SET username = ?, email = ?, phone = ?, SName = ?, SSurname = ?, color = ?, bright=?, Grade=?
                WHERE StudentID = ?
            '''
        ss = [new_username, new_email, new_phone, new_name, new_surname, new_color, bright, new_grade, current_user.id]
        upd(s, ss)

        # Обновляем данные в текущем пользователе (current_user)
        current_user.username = new_username
        current_user.email = new_email.replace('?', '@')
        current_user.phone = new_phone
        current_user.name = new_name
        current_user.surname = new_surname
        current_user.color = new_color
        current_user.bright = bright
        current_user.grade = new_grade
        flash("Профиль успешно обновлен.", "success")
        return redirect(url_for('myprofile'))


# @app.route('/results')
# def res(results, show):
#     return render_template('results.html', tasks=tasks, res=results, show=show, theme=theme)


@app.route('/test/<int:num>', methods=['POST', 'GET'])
def test(num):
    s = 'select * from Problem where Type = ?'
    x = get_data(s, [num])
    b = []
    for i in x:
        k = list(i)
        if k[8] == None:
            k[8] = ""
        if k[9] == None:
            k[9] = ""
        k[8] = k[8].split()
        k[9] = k[9].split()
        b.append(k)
    x = b
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
                res = [int(name), 0, 0, current_user.id, cur_time]
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
                current_user.results = get_user_result(current_user.id)
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
        return render_template('results.html', tasks=x, res=results,  showAns=show, showScore=True, right=rcount, theme=theme, **currentuser, loggedin=loggedin)


@login_required
@app.route('/work/<int:workid>/<int:groupid>', methods=['POST', 'GET'])
def work(workid, groupid):
    s = 'select ShowAns, ShowScore from WorkGroup where WorkID=? and GroupID=?'
    dt = get_data(s, [workid, groupid])
    dt = dt[0]
    s = '''select Problem.ProblemID, Statement, Answer, Type, Creator, Solution, code, Diff, filename, img
        from Problem join WorkProblem on Problem.ProblemID = WorkProblem.ProblemID where WorkID = ?'''
    tasks = get_data(s, [workid])
    b = []
    for i in tasks:
        k = list(i)
        if k[8] == None:
            k[8] = ""
        if k[9] == None:
            k[9] = ""
        k[8] = k[8].split()
        k[9] = k[9].split()
        b.append(k)
    tasks = b
    o = len(tasks)
    if request.method == "GET":
        return render_template('test.html', tasks=tasks, theme=theme, loggedin=loggedin, currentuser=currentuser, if_work=True)
    elif request.method == 'POST':
        cur_time = timegm(gmtime())
        results = []
        rcount = 0
        for i in range(o):
            results.append([0, 0, 0])
        for i in range(o):
            name = f'{tasks[i][0]}'
            s = 'insert into WorkResult (ProblemID, WorkID, GroupID, StudentID, date, result) values (?, ?, ?, ?, ?, ?)'
            res = [int(name), workid, groupid, current_user.id, cur_time]
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
        current_user.results = get_user_result(current_user.id)
        return render_template('results.html', tasks=tasks, res=results, showAns=dt[0], showScore=dt[1], right=rcount, theme=theme,
                           loggedin=loggedin)


@app.route('/train/<int:num>', methods=['POST', 'GET'])
def train(num):
    s = 'select * from Problem where Type = ?'
    x = get_data(s, [num])
    b = []
    if request.method == 'GET':
        for i in x:
            k = list(i)
            if k[8] == None:
                k[8] = ""
            if k[9] == None:
                k[9] = ""
            k[8] = k[8].split()
            k[9] = k[9].split()
            b.append(k)
    x = b
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
        allowed = ('jpg', 'png', 'jpeg', 'docx', 'doc', 'xls', 'xlsx', 'txt', 'csv')
        statement = request.form['stat']
        answer = request.form['ans']
        solution = request.form['sol'].replace('\n', '<br>')
        diff = request.form['diff']
        typ = int(request.form['type'])
        creator = request.form['author']
        files = request.files.getlist('file')
        imgs = request.files.getlist('img')
        dbfiles = ""
        s = 'select * from Problem where Statement=?'
        a = get_data(s, [statement])
        if diff == 'base':
            diff = 1
        elif diff == 'ke':
            diff = 3
        else:
            diff = 2
        if a != []:
            return render_template('add.html', theme=theme, **currentuser, loggedin=loggedin, message='Задача с таким условием уже есть :(')
        s = 'insert into Problem (Statement, Answer, Type, Creator, Solution, Diff) values (?, ?, ?, ?, ?, ?)'
        a = [statement, answer, typ, creator, solution, diff]
        insrt(a, s)
        cnt = 0
        s = 'select ProblemID from Problem where Statement=?'
        a = get_data(s, [statement])
        while type(a) is not int:
            a = a[0]
        for file in files:
            if file.filename == '':
                continue
            if file.filename.split('.')[1] not in allowed:
                return render_template('add.html', theme=theme, **currentuser, loggedin=loggedin,
                                       message='Вы прикрепили файл с недопустимым разрешением :(')
            path = 'static/files/problem' + str(a) + '0' + str(cnt) + '.' + file.filename.split('.')[1]
            file.save(path)
            dbfiles += path[7:] + ' '
            cnt += 1
        s = 'update Problem set filename=? where ProblemID=?'
        upd(s, [dbfiles, a])
        cnt = 0
        imgss = ""
        for file in imgs:
            if file.filename == '':
                continue
            if file.filename.split('.')[1] not in allowed:
                return render_template('add.html', theme=theme, **currentuser, loggedin=loggedin,
                                       message=f'Вы прикрепили файл с недопустимым разрешением ({file.filename.split(".")[1]}) :(')
            path = 'static/files/problem' + str(a) + '1' + str(cnt) + '.' + file.filename.split('.')[1]
            file.save(path)
            imgss += path[7:] + ' '
            cnt += 1
        s = 'update Problem set img="? where ProblemID=?'
        upd(s, [imgss, a])
        return redirect(url_for('index'))


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
    a = get_data(s, [])
    return render_template('courses.html', courses=a, theme=theme, **currentuser, loggedin=loggedin)


@login_required
@app.route('/enter/<int:id>')
def enter_course(id):
    s = 'select distinct StudID from CourseStud where CID=?'
    a = get_data(s, [id])
    for i in a:
        if current_user.id in i:
            return redirect(url_for('course', id=id, num=1))
    s = 'insert into CourseStud (CID, StudID) values (?, ?)'
    a = [id, current_user.id]
    insrt(a, s)
    return redirect(url_for('course', id=id, num=1))


@app.route('/forum', methods=['POST', 'GET'])
def forum():
    s = f"select * from Questions order by date desc"
    a = get_data(s, [])
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
        b = []
        o = {}  # фильтрация по времени
        for key in request.form:
            if key != 'txt':
                if request.form[key] == '':
                    o[key] = 0
                else:
                    o[key] = int(request.form[key])
        txt = request.form['txt']
        delta = 60 * o['min'] + 3600 * o['hour'] + 86400 * o['day'] + 2629743 * o['month'] + 31556926 * o['year']
        if delta == 0:
            delta = 1737647353
        for i in a:
            k = list(i)
            dd = i[3]
            ss = gmtime(dd)
            ss = asctime(ss)
            ss = str(ss)
            k[3] = ss[4:16] + ss[19:]
            if (dd + delta >= tm and dd <= tm) and (txt != None and txt in i[2]):
                b.append(k)
        return render_template('forum.html', category="Выбранные", questions=b, theme=theme, **o, **currentuser, loggedin=loggedin, txt=txt)
    return render_template('forum.html', category="Недавние", questions=b, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/question/<int:qid>', methods=['POST', 'GET'])
def ans(qid):
    s1 = 'select * from Questions where QID = ?'
    x1 = get_data(s1, [qid])
    if request.method == 'POST':
        if current_user.is_authenticated:
            username = current_user.username
        else:
            username = "неизвестный"
        tm = timegm(gmtime())
        text = request.form['answer']
        s = 'insert into Answers (QID, Author, Statement, date) values (?, ?, ?, ?)'
        a = [qid, username, text, tm]
        insrt(a, s)
    s2 = 'select * from Answers where QID = ? order by date desc'
    x2 = get_data(s2, [qid])
    q = list(x1[0])
    dd = x1[0][3]
    ss = gmtime(dd)
    ss = asctime(ss)
    ss = str(ss)
    q[3] = ss[4:16] + ss[19:]
    return render_template('question.html', answers=x2, question=q, theme=theme, **currentuser, loggedin=loggedin)


@app.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    if current_user.adm == 1:
        s = 'DELETE FROM Answers WHERE AId = ?'
        upd(s, [comment_id])
        return redirect(request.referrer)  # Возвращаем пользователя на предыдущую страницу
    else:
        return "У вас нет прав для выполнения этого действия", 403


@app.route('/delete_post/<int:qid>')
@login_required
def delete_post(qid):
    if current_user.adm == 1:
        s1 = 'DELETE FROM Answers WHERE QID = ?'
        upd(s1, [qid])
        s2 = 'DELETE FROM Questions WHERE QID = ?'
        upd(s2, [qid])
        return redirect(url_for('forum'))
    else:
        return "У вас нет прав для выполнения этого действия", 403


@app.route('/close_post/<int:qid>')
@login_required
def close_post(qid):
    if current_user.adm == 1:
        s = 'UPDATE Questions SET Open = 0 WHERE QID = ?'
        upd(s, [qid])
        return redirect(request.referrer)
    else:
        return "У вас нет прав для выполнения этого действия", 403


@app.route('/open_post/<int:qid>')
@login_required
def open_post(qid):
    if current_user.adm == 1:
        s = 'UPDATE Questions SET Open = 1 WHERE QID = ?'
        upd(s, [qid])
        return redirect(request.referrer)
    else:
        return "У вас нет прав для выполнения этого действия", 403


@app.route('/course/<int:id>/<int:num>')
def course(id, num):
    s = 'select distinct Type from CourseMaterial join Courses on Courses.CID = CourseMaterial.CID where Courses.CID = ? order by Type asc'
    a = get_data(s, [id])
    types = []
    for i in a:
        types.append(i[0])
    s = 'select Courses.CID, CName, Type, Link, text, lang, code, files from CourseMaterial join Courses on Courses.CID = CourseMaterial.CID where Courses.CID = ? and Type=?'
    a = get_data(s, [id, num])
    if len(a) == 1:
        a = a[0]
    b = list(a)
    return render_template('course.html', course=b, theme=theme, types=types)


@login_required
@app.route('/ask', methods=['POST', 'GET'])
def ask():
    if request.method == 'GET':
        return render_template('ask.html', theme=theme, **currentuser, loggedin=loggedin)
    if request.method == 'POST':
        question = request.form['q']
        if current_user.is_authenticated:
            username = current_user.username
        else:
            username = "неизвестный"
        tm = timegm(gmtime())
        s = 'insert into Questions (Author, Statement, date, Open) values (?, ?, ?, ?)'
        a = [username, question, tm, 1]
        insrt(a, s)
        s = 'select QID from Questions where date = ?'
        x = get_data(s, [tm])
        x = x[0]
        return render_template('tea.html', theme=theme, **currentuser, loggedin=loggedin)
    return render_template('ask.html', theme=theme, **currentuser, loggedin=loggedin)


@app.route('/bank', methods=['POST', 'GET'])
def bank():
    s = f"select * from Problem order by Type asc, Diff "
    a = get_data(s, [])
    b = []
    tm = timegm(gmtime())
    if request.method == 'GET':
        for i in a:
            k = list(i)
            if k[8] == None:
                k[8] = ""
            if k[9] == None:
                k[9] = ""
            k[8] = k[8].split()
            k[9] = k[9].split()
            b.append(k)
        return render_template('bank.html', category="Все", tasks=b, theme=theme, **currentuser, loggedin=loggedin)
    elif request.method == 'POST':
        b = []
        kim = request.form['kim']
        diff = request.form['diff']
        txt = request.form['txt']
        for i in a:
            k = list(i)
            if k[8] == None:
                k[8] = ""
            if k[9] == None:
                k[9] = ""
            k[8] = k[8].split()
            k[9] = k[9].split()
            if (len(kim) != 0 and k[3] == int(kim)) or len(kim) == 0:
                if (len(diff) != 0 and k[7] == int(diff)) or len(diff) == 0:
                    if (len(txt) != 0 and txt in k[1]) or len(txt) == 0:
                        b.append(k)
        if kim != '':
            n = int(kim)
        else:
            n = 0
        if diff != '':
            d = int(diff)
        else:
            d = 0
        return render_template('bank.html', category="Выбранные", tasks=b, theme=theme, **currentuser, loggedin=loggedin, n=n, d=d, txt=txt)


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
        s = 'select GroupID from Groups where GroupName = ?'
        a = get_data(s, [name])
        if a !=[]:
            return render_template('add_group.html', message='Группа с таким названием уже есть', theme=theme, **currentuser, loggedin=loggedin)
        s = 'insert into Groups (GroupName) values (?)'
        a = [name]
        insrt(a, s)
        s = 'select GroupID from Groups where GroupName = ?'
        a = get_data(s, name)
        a = a[0]
        if type(a) is not int:
            id = a[0]
        else:
            id = a
        s = 'insert into GroupTeacher (GroupID, CreatorID) values (?, ?)'
        a = [id, current_user.id]
        insrt(a, s)
        if teachers != []:
            for user in teachers:
                if ',' in user:
                    user = user.replace(',', '')
                s = 'select StudentID from Users where username=?'
                a = get_data(s, [user])
                a = a[0]
                if type(a) is not int:
                    id1 = a[0]
                else:
                    id1 = a
                s = 'insert into GroupTeacher (GroupID, CreatorID) values (?, ?)'
                a = [id, id1]
                insrt(a, s)
        for user in students:
            if ',' in user:
                user = user.replace(',', '')
            s = 'select StudentID from Users where username=?'
            a = get_data(s, [user])
            a = a[0]
            if type(a) is not int:
                id1 = a[0]
            else:
                id1 = a
            s = 'insert into GroupStud (GroupID, StudID) values (?, ?)'
            a = [id, id1]
            insrt(a, s)
        return render_template('tea.html', theme=theme, loggedin=loggedin, **currentuser)


@login_required
@app.route('/dashboard/<int:id>')
def dashboard(id):
    s = 'select GroupName from Groups where GroupID = ?'
    a = get_data(s, [id])
    a = a[0]
    if type(a) is not str:
        GName = a[0]
    else:
        GName = a
    s = 'select SName, SSurname, username from GroupTeacher join Users on GroupTeacher.CreatorID = Users.StudentID where GroupID = ?'
    teachers = get_data(s, [id])
    teacher = False
    for i in teachers:
        if current_user.username in i:
            teacher = True
            break
    s = 'select SName, SSurname, username from GroupStud join Users on GroupStud.StudID = Users.StudentID where GroupID = ?'
    students = get_data(s, [id])
    s = 'select Work.WorkID, CreatorID, WorkName from WorkGroup join Work on WorkGroup.WorkID = Work.WorkID where GroupID = ?'
    works = get_data(s, [id])
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

        s = 'insert into Work (CreatorID, WorkName) values (?, ?)'
        a = [id, answer]
        insrt(a, s)

        sW = 'select * from Work order by CreatorID'
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
            s1 = 'insert into WorkProblem (WorkID, ProblemID) values (?, ?)'
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
                s = 'select StudentID from Users where username=?'
                a = get_data(s, [user])
                a = a[0]
                if type(a) is not int:
                    id1 = a[0]
                else:
                    id1 = a
                s = 'select GroupID, CreatorID from GroupTeacher where CreatorID=? and GroupID=?'
                a = get_data(s, [id1, id])
                if a == []:
                    s = 'insert into GroupTeacher (GroupID, CreatorID) values (?, ?)'
                    a = [id, id1]
                    insrt(a, s)
        for user in students:
            if ',' in user:
                user = user.replace(',', '')
            s = 'select StudentID from Users where username=?'
            a = get_data(s, [user])
            a = a[0]
            if type(a) is not int:
                id1 = a[0]
            else:
                id1 = a
            s = 'select GroupID, StudID from GroupStud where StudID=? and GroupID=?'
            a = get_data(s, [id1, id])
            if a == []:
                s = 'insert into GroupStud (GroupID, StudID) values (?, ?)'
                a = [id, id1]
                insrt(a, s)
        return redirect(url_for('dashboard', id=id))


@login_required
@app.route('/work_results/<int:workid>/<int:groupid>')
def work_result(workid, groupid):
    s = 'select distinct CreatorID from GroupTeacher where GroupID=?'
    ss = [groupid]
    a = get_data(s, ss)
    teachers = []
    for i in a:
        teachers.append(i[0])
    if current_user.id in teachers:
        results = get_group_result_work(groupid, workid)
        s = 'select WorkName from Work where WorkID = ?'
        ss = [workid]
        a = get_data(s, ss)
        while type(a) is not str:
            a = a[0]
        work_name = a
        s = 'select GroupName from Groups where GroupID = ?'
        ss = [groupid]
        a = get_data(s, ss)
        while type(a) is not str:
            a = a[0]
        group_name = a
        return render_template('work_results.html',  theme=theme, **currentuser, loggedin=loggedin, group_name=group_name, work_name=work_name, work_results=results)
    else:
        #return redirect(url_for('restricted'))
        return redirect(url_for('error'))


@login_required
@app.route('/my_group/<int:groupid>')
def my_group(groupid):
    results = get_user_results_in_group(current_user.id, groupid)
    return render_template('user_results.html', theme=theme, results=results)


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
