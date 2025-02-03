import _sqlite3
from time import *
from calendar import *


def get_user_by_id(user_id):
    s = f"select * from Users where StudentID = {user_id}"
    a = get_data(s)
    a = a[0]
    a = list(a)
    a.append(get_user_result(user_id))
    return a


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


def get_my(id):
    s = f'select * from PrepCourse join Courses on PrepCourse.CID = Courses.CID where PrepID={id}'
    a = get_data(s)
    b = []
    for i in a:
        k = list(i)
        temp = []
        temp.append(k[0])
        for j in k[2:]:
            temp.append(j)
        k = temp
        b.append(k)
    s = f'select * from Groups join GroupTeacher on Groups.GroupID = GroupTeacher.GroupID where GroupTeacher.CreatorID = {id}'
    a = get_data(s)
    c = []
    for i in a:
        k = list(i)
        k = k[:-1]
        c.append(k)
    s = f'select * from Work where CreatorID={id}'
    a = get_data(s)
    d = []
    for i in a:
        k = list(i)
        d.append(k)
    for i in a:
        k = list(i)
        d.append(k)
    s = f'select * from CourseStud join Courses on CourseStud.CID = Courses.CID where StudID={id}'
    a = get_data(s)
    e = []
    for i in a:
        k = list(i)
        temp = []
        k = k[2:]
        e.append(k)
    s = f'select * from Groups join GroupStud on Groups.GroupID = GroupStud.GroupID where GroupStud.StudID = {id}'
    a = get_data(s)
    f = []
    for i in a:
        k = list(i)
        k = k[:-1]
        f.append(k)
    s = f'select WorkGroup.WorkID, WorkName from Work join WorkGroup on Work.WorkID = WorkGroup.WorkID join GroupStud on WorkGroup.GroupID = GroupStud.GroupID where StudID = {id}'
    a = get_data(s)
    g = []
    for i in a:
        k = list(i)
        g.append(k)
    r = [b, c, d, e, f, g]
    return r


def upd(s):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(s)
    c.commit()
    c.close()


def get_user_result_work(userid, groupid, workid, timer=timegm(gmtime())):
    template = ['name', 'surname']
    s = f'select SSurname, SName from Users where StudentID = {userid}'
    a = get_data(s)
    template = [a[0][0], a[0][1]]
    s = f'select count(ProblemID) from WorkProblem where WorkID = {workid}'
    a = get_data(s)
    while type(a) is not int:
        a = a[0]
    n = a
    cur_time = timegm(gmtime())
    s = f'''select distinct ProblemID, StudentID, result
        from WorkResult
        where date >= {cur_time - timer} and GroupID={groupid} and WorkID={workid} and StudentID="{userid}" 
        order by ProblemID desc, date desc'''
    a = get_data(s)
    total = 0
    for i in a:
        template.append(i[2])
        total += i[2]
    template.append(total)
    template.append(n)
    return template


def get_user_result(userid, timer=timegm(gmtime())):
    cur_time = timegm(gmtime())
    res = []
    for i in range(1, 28):
        s = f'select count(result) from WorkResult join Problem on Problem.ProblemID = WorkResult.ProblemID where StudentID={userid} and Type={i} and date >= {cur_time - timer}'
        a = get_data(s)
        n_i = a[0][0]
        s = f'select count(result) from WorkResult join Problem on Problem.ProblemID = WorkResult.ProblemID where StudentID={userid} and Type={i} and date >= {cur_time - timer} and result=1'
        a = get_data(s)
        r_i = a[0][0]
        res.append([r_i, n_i])
    return res


def get_group_result_work(groupid, workid, timer=timegm(gmtime())):
    cur_time = timegm(gmtime())
    title = ['Имя', 'Фамилия']
    s = f'select ProblemID from WorkProblem where WorkID = {workid} order by ProblemID desc'
    a = get_data(s)
    for i in a:
        title.append(i[0])
    n = len(title) - 2
    title.append('Всего верных')
    title.append('Всего задач')
    res = [title]
    s = f'select distinct StudentID from WorkResult where WorkID={workid} and GroupID={groupid} and date >= {cur_time - timer}'
    a = get_data(s)
    students = []
    for i in a:
        students.append(i[0])
    for stud in students:
        res.append(get_user_result_work(stud, groupid, workid, timer))
    return res


def get_group_result(groupid, timer=timegm(gmtime())):
    res = []
    for i in range(27):
        res.append([0, 0])
    s = f'select distinct StudID from GroupStud where GroupID={groupid}'
    a = get_data(s)
    students = []
    for i in a:
        students.append(i[0])
    for stud in students:
        rr = get_user_result(stud, timer)
        for i in range(27):
            res[i][0] += rr[i][0]
            res[i][1] += rr[i][1]
    return res


def get_user(username=None, email = None):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    what = f"select * from Users where username = '{username}'"
    what1 = f"select * from Users where username = '{email}'"
    curs.execute(what)
    line = curs.fetchall()
    c.commit()
    c.close()
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(what1)
    line2 = curs.fetchall()
    c.commit()
    c.close()
    if len(line) == 1:
        line = line[0]
    if len(line2) == 1:
        line2 = line2[0]
    if len(line) == 0 and len(line2) == 0:
        return 'No such user'
    x = line
    if len(line) == 0:
        x = line2
    user = {
        "StudentID": x[0],
        "username": x[1],
        "email": x[2].replace('?', '@'),
        "phone": x[3],
        "password": x[4],
        "name": x[5],
        "surname": x[6],
        "grade": x[7],
        "color": x[8],
        "bright": x[10],
        "adm": x[10]
    }
    user['results'] = get_user_result(user['StudentID'])
    return user


def get_user_results_in_group(userid, groupid, timer=timegm(gmtime())):
    works = []
    s = f'select distinct workID from WorkGroup where GroupID = {groupid} and ShowScore=1'
    a = get_data(s)
    for i in a:
        works.append(i[0])
    results = []
    for workid in works:
        template = []
        t = []
        s = f'select count(distinct ProblemID) from WorkProblem where WorkID = {workid}'
        a = get_data(s)
        if not a:
            continue
        while type(a) is not int:
            a = a[0]
        n = a
        s = f'select distinct ProblemID from WorkProblem where WorkID = {workid} order by ProblemID desc'
        a = get_data(s)
        t.append(a)
        s = f'select WorkName from Work where WorkID={workid}'
        a = get_data(s)
        if not a:
            return []
        while type(a) is not str:
            a = a[0]
        b = ["Название работы"]
        for i in a:
            b.append(i[0])
        b.append("Всего решено")
        b.append("Всего")
        a = b
        template.append(a)
        cur_time = timegm(gmtime())
        s = f'''select distinct ProblemID, StudentID, result
            from WorkResult
            where date >= {cur_time - timer} and GroupID={groupid} and WorkID={workid} and StudentID="{userid}" 
            order by ProblemID desc, date desc'''
        a = get_data(s)
        total = 0
        x = {}
        for i in a:
            x[i[0]] = i[2]
        for i in a:
            template.append(max(i[2], x[i[0]]))
            total += i[2]
        template.append(total)
        template.append(n)
        t.append(template)
        results.append(t)
    return results

