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
    print(a)
    b = []
    for i in a:
        k = list(i)
        k = k[2:]
        b.append(k)
    s = f'select * from Group join GroupTeacher on Group.GroupID = GroupTeacher.GroupID where GroupTeacher.CreatorID = {id}'
    a = get_data(s)
    print(a)
    c = []
    for i in a:
        k = list(i)
        k = k[2:]
        c.append(k)
    s = f'select * from Work CreatorID={id}'
    a = get_data(s)
    print(a)
    d = []
    for i in a:
        k = list(i)
        k = k[2:]
        d.append(k)
    r = [b, c, d]
    return r