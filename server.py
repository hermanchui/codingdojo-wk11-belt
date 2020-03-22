from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
import re  # the regex module    
from flask_bcrypt import Bcrypt 

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
PWD_REGEX = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!*#?&])[A-Za-z\d@$!#*?&]{6,20}$")
app = Flask(__name__)
app.secret_key = "afdshjklfjopterwwiogf"
bcrypt = Bcrypt(app)    # we are creating an object called bcrypt, 
                        # which is made by invoking the function Bcrypt with our app as an argument

@app.route('/')
def login_registration():
    return render_template('login-registration.html')
    
@app.route('/add-user', methods = ['POST'])
def add_user_action():
    first_name = request.form['fname']
    last_name = request.form['lname']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirmation']

    if len(first_name) == 0:
        flash("Please enter a first name.")
    elif not first_name.isalpha():
        flash("First name must be all letters.")
    elif len(last_name) == 0:
        flash("Please enter a last name.")
    elif not last_name.isalpha():
        flash("Last name must be all letters.")
    elif not EMAIL_REGEX.match(email):    # test whether a field matches the pattern
        flash("Invalid email address.")
    elif not re.search(PWD_REGEX, password): 
        flash("Password must be 6-20 characters and contain one or more of each of: a number, uppercase letter, lower case letter, and special symbol.")
    elif password != confirm:
        flash("Password confirmation does not match.")
    else:
        mySQL = connectToMySQL('exam-wish-app')
        query = "INSERT INTO users (first_name, last_name, email, pwd_hash, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pwd)s, NOW(), NOW());"
        data = {
            'fn': first_name,
            'ln': last_name,
            'em': email,
            'pwd': bcrypt.generate_password_hash(password)
        }
        mySQL.query_db(query, data)
        flash("New user added.")
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    mySQL = connectToMySQL('exam-wish-app')
    query = "SELECT * FROM users WHERE email = %(em)s;"
    data = {
        'em': request.form['email']
    }
    result = mySQL.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['pwd_hash'], request.form['password']):
            session['userid'] = result[0]['id']
            session['first_name'] = result[0]['first_name']
            return redirect('/wishes')
        else:
            flash("Login failed.")
    else:
        flash("Unknown user.")
    return redirect('/')

@app.route('/wishes')
def show_wishes():
    if 'userid' in session:
        user_id = session['userid']
        # get pending wishes for current user
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT * FROM wishes WHERE user_id = %(uid)s AND is_granted = FALSE ORDER BY created_at DESC;"
        data = {
            'uid': user_id
        }
        wishes = mySQL.query_db(query, data)
        # get granted wishes for all users
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT wishes.id as id, item, users.first_name as first_name, description, wishes.created_at as created_at, granted_at, COUNT(likes.id) AS likes FROM wishes JOIN users ON wishes.user_id = users.id LEFT JOIN likes ON wishes.id = likes.wish_id WHERE is_granted = TRUE GROUP BY wishes.id ORDER BY wishes.granted_at DESC;"
        granted = mySQL.query_db(query)
        return render_template('wishes.html', wishes = wishes, granted = granted)
    else:
        return redirect('/')

@app.route('/wishes/new')
def new_wish():
    if 'userid' in session:
        return render_template('new_wish.html')
    else:
        return redirect('/')

@app.route('/wishes/add', methods = ['POST'])
def add_wish():
    if 'userid' in session:
        item = request.form['item']
        description = request.form['description']
        user_id = session['userid']
        if len(item) < 3:
            flash("A wish must consist of at least 3 characters!")
        if len(description) < 3:
            flash("A description must consist of at least 3 characters!")
        if '_flashes' not in session:
            mySQL = connectToMySQL('exam-wish-app')
            query = "INSERT INTO wishes (item, description, is_granted, granted_at, user_id, created_at, updated_at) VALUES (%(item)s, %(desc)s, FALSE, NULL, %(uid)s, NOW(), NOW());"
            data = {
                'item': item,
                'desc': description,
                'uid': user_id
            }
            mySQL.query_db(query, data)
            return redirect('/wishes')
        return redirect('/wishes/new')
    else:
        return redirect('/')

@app.route('/wishes/remove/<wish_id>')
def remove_wish(wish_id):
    if 'userid' in session:
        user_id = session['userid']
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT * FROM wishes WHERE id = %(id)s;"
        data = {
            'id': wish_id
        }
        wishes = mySQL.query_db(query, data)
        if len(wishes) == 0:
            flash("Wish not found!")
            return redirect('/wishes')
        elif wishes[0]['user_id'] != user_id:  # owner of wish does not match logged in user
            flash("Cannot delete another user's wish!")
            return redirect('/wishes')
        mySQL = connectToMySQL('exam-wish-app')
        query = "DELETE FROM wishes WHERE id = %(id)s;"
        data = {
            'id': wish_id
        }
        mySQL.query_db(query, data)
        return redirect('/wishes')
    else:
        return redirect('/')

@app.route('/wishes/edit/<wish_id>')
def edit_wish(wish_id):
    if 'userid' in session:
        user_id = session['userid']
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT * FROM wishes WHERE id = %(id)s;"
        data = {
            'id': wish_id
        }
        wishes = mySQL.query_db(query, data)
        if len(wishes) == 0:
            flash("Wish not found!")
            return redirect('/wishes')
        elif wishes[0]['user_id'] != user_id:  # owner of wish does not match logged in user
            flash("Cannot edit another user's wish!")
            return redirect('/wishes')
        return render_template('edit_wish.html', wish = wishes[0])
    else:
        return redirect('/')

@app.route('/wishes/update/<wish_id>', methods = ['POST'])
def update_wish(wish_id):
    if 'userid' in session:
        item = request.form['item']
        description = request.form['description']
        user_id = session['userid']
        if len(item) < 3:
            flash("A wish must consist of at least 3 characters!")
        if len(description) < 3:
            flash("A description must consist of at least 3 characters!")
        if '_flashes' not in session:
            mySQL = connectToMySQL('exam-wish-app')
            query = "SELECT * FROM wishes WHERE id = %(id)s;"
            data = {
                'id': wish_id
            }
            wishes = mySQL.query_db(query, data)
            if len(wishes) == 0:
                flash("Wish not found!")
                return redirect('/wishes')
            elif wishes[0]['user_id'] != user_id:  # owner of wish does not match logged in user
                flash("Cannot update another user's wish!")
                return redirect('/wishes')
            mySQL = connectToMySQL('exam-wish-app')
            query = "UPDATE wishes SET item = %(item)s, description = %(desc)s, updated_at = NOW() WHERE id = %(id)s;"
            data = {
                'item': item,
                'desc': description,
                'id': wish_id
            }
            mySQL.query_db(query, data)
            return redirect('/wishes')
        return redirect('/wishes/edit/'+str(wish_id))
    else:
        return redirect('/')

@app.route('/wishes/like/<wish_id>')
def like_wish(wish_id):
    if 'userid' in session:
        user_id = session['userid']
        # check if already liked and reject if is
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT * FROM likes WHERE user_id = %(uid)s AND wish_id = %(wid)s;"
        data = {
            'wid': wish_id,
            'uid': user_id
        }
        result = mySQL.query_db(query, data)
        if len(result) > 0:
            flash("Already liked!")
            return redirect('/wishes')

        # check if like is for current user and reject if is
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT * FROM wishes WHERE user_id = %(uid)s AND id = %(wid)s;"
        data = {
            'wid': wish_id,
            'uid': user_id
        }
        result = mySQL.query_db(query, data)
        if len(result) > 0:
            flash("Cannot like your own wish!")
            return redirect('/wishes')

        mySQL = connectToMySQL('exam-wish-app')
        query = "INSERT INTO likes (wish_id, user_id, created_at, updated_at) VALUES (%(wid)s, %(uid)s, NOW(), NOW());"
        data = {
            'wid': wish_id,
            'uid': user_id
        }
        mySQL.query_db(query, data)

        return redirect('/wishes')
    return redirect('/')

@app.route('/wishes/grant/<wish_id>')
def grant_wish(wish_id):
    if 'userid' in session:
        user_id = session['userid']
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT * FROM wishes WHERE id = %(id)s;"
        data = {
            'id': wish_id
        }
        wishes = mySQL.query_db(query, data)
        if len(wishes) == 0:
            flash("Wish not found!")
            return redirect('/wishes')
        elif wishes[0]['user_id'] != user_id:  # owner of wish does not match logged in user
            flash("Cannot grant another user's wish!")
            return redirect('/wishes')
        mySQL = connectToMySQL('exam-wish-app')
        query = "UPDATE wishes SET is_granted = TRUE, granted_at = NOW() WHERE id = %(id)s;"
        data = {
            'id': wish_id
        }
        mySQL.query_db(query, data)
        return redirect('/wishes')
    else:
        return redirect('/')

@app.route('/wishes/stats')
def show_wish_stats():
    if 'userid' in session:
        user_id = session['userid']
        # get total number of granted wishes
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT COUNT(id) AS count FROM wishes WHERE is_granted = TRUE;"
        data = {
            'uid': user_id
        }
        total_result = mySQL.query_db(query, data)
        if total_result:
            total = total_result[0]['count']
        else:
            total = 0
        # get number of pending wishes for this user
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT COUNT(id) AS count FROM wishes WHERE user_id = %(uid)s and is_granted = FALSE GROUP BY user_id = %(uid)s;"
        data = {
            'uid': user_id
        }
        pending_result = mySQL.query_db(query, data)
        if pending_result:
            pending = pending_result[0]['count']
        else:
            pending = 0
        # get number of granted wishes for this user
        mySQL = connectToMySQL('exam-wish-app')
        query = "SELECT COUNT(id) AS count FROM wishes WHERE user_id = %(uid)s and is_granted = TRUE GROUP BY user_id = %(uid)s;"
        data = {
            'uid': user_id
        }
        granted_result = mySQL.query_db(query, data)
        if granted_result:
            granted = granted_result[0]['count']
        else:
            granted = 0
        return render_template('stats.html', total = total, granted = granted, pending = pending)
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)