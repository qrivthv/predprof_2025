import _sqlite3


def get_data(what):
    c = _sqlite3.connect('db.db')
    curs = c.cursor()
    curs.execute(what)
    line = curs.fetchall()
    c.commit()
    c.close()
    return line


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
        "color": x[9],
        "bright": x[10]
    }
    r = []
    k = 0
    n = 0
    if len(x) == 0:
        r = []
    else:
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
    user['results'] = r
    return user


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

def get_group_result(groupid):
    pass


def get_user_result(userid):
    pass