import _sqlite3
from time import *
from calendar import *


def get_user_by_id(user_id):
    s = "select * from Users where StudentID = ?"
    ss = [user_id]
    a = get_data(s, ss)
    a = a[0]
    a = list(a)
    a.append(get_user_result(user_id))
    return a


def get_data(what, base):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(what, base)
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
    ss = [id]
    s = 'select * from PrepCourse join Courses on PrepCourse.CID = Courses.CID where PrepID=?'
    a = get_data(s, ss)
    b = []
    for i in a:
        k = list(i)
        temp = []
        temp.append(k[0])
        for j in k[2:]:
            temp.append(j)
        k = temp
        b.append(k)
    s = 'select * from Groups join GroupTeacher on Groups.GroupID = GroupTeacher.GroupID where GroupTeacher.CreatorID = ?'
    a = get_data(s, ss)
    c = []
    for i in a:
        k = list(i)
        k = k[:-1]
        c.append(k)
    s = 'select * from Work where CreatorID=?'
    a = get_data(s, ss)
    d = []
    for i in a:
        k = list(i)
        d.append(k)
    for i in a:
        k = list(i)
        d.append(k)
    s = 'select * from CourseStud join Courses on CourseStud.CID = Courses.CID where StudID=?'
    a = get_data(s, ss)
    e = []
    for i in a:
        k = list(i)
        temp = []
        k = k[2:]
        e.append(k)
    s = 'select * from Groups join GroupStud on Groups.GroupID = GroupStud.GroupID where GroupStud.StudID = ?'
    a = get_data(s, ss)
    f = []
    for i in a:
        k = list(i)
        k = k[:-1]
        f.append(k)
    s = 'select WorkGroup.WorkID, WorkName from Work join WorkGroup on Work.WorkID = WorkGroup.WorkID join GroupStud on WorkGroup.GroupID = GroupStud.GroupID where StudID = ?'
    a = get_data(s, ss)
    g = []
    for i in a:
        k = list(i)
        g.append(k)
    r = [b, c, d, e, f, g]
    return r


def upd(s, data):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(s, data)
    c.commit()
    c.close()


def get_user_result_work(userid, groupid, workid, timer=timegm(gmtime())):
    template = ['name', 'surname']
    ss = [userid]
    s = 'select SSurname, SName from Users where StudentID = ?'
    a = get_data(s, ss)
    template = [a[0][0], a[0][1]]
    ss = [workid]
    s = 'select count(ProblemID) from WorkProblem where WorkID = ?'
    a = get_data(s, ss)
    while type(a) is not int:
        a = a[0]
    n = a
    cur_time = timegm(gmtime())
    s = '''select distinct ProblemID, StudentID, result, date
        from WorkResult
        where date >= ? and GroupID=? and WorkID = ? and StudentID= ?
        order by date desc, ProblemID desc'''
    ss = [cur_time - timer, groupid, workid, userid]
    a = get_data(s, ss)
    total = 0
    dates = []
    for i in a:
        if i[3] not in dates:
            dates.append(i[3])
    if len(dates) > 1:
        date = max(dates)
    else:
        date = dates[0]
    for i in a:
        if i[3] == date:
            template.append(i[2])
            total += i[2]
    template.append(total)
    template.append(n)
    return template


def get_user_result(userid, timer=timegm(gmtime())):
    cur_time = timegm(gmtime())
    res = []
    for i in range(1, 28):
        s = 'select count(result) from WorkResult join Problem on Problem.ProblemID = WorkResult.ProblemID where StudentID=? and Type=? and date >= ?'
        ss = [userid, i, cur_time - timer]
        a = get_data(s, ss)
        n_i = a[0][0] if a else 0
        s = 'select count(result) from WorkResult join Problem on Problem.ProblemID = WorkResult.ProblemID where StudentID = ? and Type = ? and date >= ? and result=1'
        a = get_data(s, ss)
        r_i = a[0][0] if a else 0
        res.append([r_i, n_i])
    return res


def get_group_result_work(groupid, workid, timer=timegm(gmtime())):
    cur_time = timegm(gmtime())
    title = ['Имя', 'Фамилия']
    ss = [workid]
    s = 'select ProblemID from WorkProblem where WorkID = ? order by ProblemID desc'
    a = get_data(s, ss)
    for i in a:
        title.append(i[0])
    n = len(title) - 2
    title.append('Всего верных')
    title.append('Всего задач')
    res = [title]
    s = 'select distinct StudentID from WorkResult where WorkID=? and GroupID=? and date >= ?'
    ss = [workid, groupid, cur_time - timer]
    a = get_data(s, ss)
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
    s = 'select distinct StudID from GroupStud where GroupID=?'
    ss = [groupid]
    a = get_data(s, ss)
    students = [i[0] for i in a] if a else []
    for stud in students:
        rr = get_user_result(stud, timer)
        for i in range(27):
            res[i][0] += rr[i][0]
            res[i][1] += rr[i][1]
    return res


def get_user(username=None, email = None):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    what = "select * from Users where username = ?"
    ss1 = [username]
    what1 = "select * from Users where username = ?"
    ss2 = [email]
    curs.execute(what, ss1)
    line = curs.fetchall()
    c.commit()
    c.close()
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(what1, ss2)
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
    s = 'select distinct workID from WorkGroup where GroupID = ? and ShowScore=1'
    ss = [groupid]
    a = get_data(s, ss)
    for i in a:
        works.append(i[0])
    results = []
    for workid in works:
        this_result = []
        template_result = []
        problem_ids = []
        s = 'select count(distinct ProblemID) from WorkProblem where WorkID = ?'
        ss = [workid]
        a = get_data(s, ss)
        if not a:
            continue
        n = a[0][0] if a else 0
        s = 'select distinct ProblemID from WorkProblem where WorkID = ? order by ProblemID desc'
        a = get_data(s, ss)
        problem_ids = [i[0] for i in a] if a else []
        s = 'select WorkName from Work where WorkID=?'
        a = get_data(s, ss)
        if not a:
            return []
        workName = a[0][0] if a else ""
        header = ["Название работы"] + problem_ids + ["Всего решено", "Всего"]
        template_result.append(workName)
        cur_time = timegm(gmtime())
        s = '''select distinct ProblemID, StudentID, result, date
            from WorkResult
            where date >= ? and GroupID=? and WorkID=? and StudentID=? 
            order by ProblemID desc, date desc'''
        ss = [cur_time - timer, groupid, workid, userid]
        a = get_data(s, ss)
        total = 0
        x = {}
        dates = []
        for i in a:
            if i[3] not in dates:
                dates.append(i[3])
        if len(dates) > 1:
            date = max(dates)
        else:
            date = dates[0]
        for i in a:
            x[i[0]] = i[2]
            if i[3] == date:
                template_result.append(i[2])
                total += i[2]
        template_result.append(total)
        template_result.append(n)
        this_result.append(header)
        this_result.append(template_result)
        results.append(this_result)
    return results