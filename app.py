from flask import Flask, render_template, request, flash,  redirect, url_for, session
import subprocess
from mysql.connector import connection, Error
import _mysql_connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('login.html', with_categories=False)


# for log in


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            # flash('Login successful!', 'success')
            return render_template('index.html')
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

def create_connection():
    """ create a database connection to the MySQL database """
    
    try:
        conn = connection.MySQLConnection(user='root', password='root',
                                 host='127.0.0.1',
                                 database='attendance')
        if conn.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return conn

# log out
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# login ends
@app.route('/attendance_view')
def attendance_view():
    return render_template('attendance.html', selected_date='',  no_data=False)

@app.route('/backhome')
def backhome():
    return render_template('index.html', selected_date='', no_data=False)

@app.route('/takeattendance')
def takeattendance():
    # render_template('loading.html')
    subprocess.run(["python", "attendance_taker.py"])
    return render_template('index.html', no_data=False)

@app.route('/add_student')
def add_student():
    # render_template('loading.html',selected_date='', no_data=False)
    subprocess.run(["python", "get_faces_from_camera_tkinter.py"])
    return render_template('index.html', no_data=False)
# 
# @app.route('/delete_student')
# def remove_student(): 
    # return render_template('remove.html', no_data=False,name='',roll_no='')
# 
@app.route('/delete_student', methods=['POST'])
def delete_student():
    rollno = request.form.get('roll_no')
    name=request.form.get('sname')
    subprocess.run(["python", "delete_face.py", rollno, name]) 
    return render_template('remove.html', no_data=False, name='', roll_no='')





@app.route('/search_rollno')
def search_rollno():
    return render_template('remove.html', rollno='', name='', no_data=False)

@app.route('/search_rollno',methods=['POST'])
def search_student():
    rollno = request.form.get('rollno')
    conn = connection.MySQLConnection(user='root', password='root',
                                 host='127.0.0.1',
                                 database='attendance')

    cursor = conn.cursor()

    cursor.execute("SELECT name FROM studentdetails WHERE roll_no = %s",(rollno,))
    name = cursor.fetchall()

    conn.close()

    if not name:
        return render_template('remove.html', roll_no='',name='', no_data=True)
    
    return render_template('remove.html', roll_no=rollno, name=name[0][0], no_data=False)




@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = connection.MySQLConnection(user='root', password='root',
                                 host='127.0.0.1',
                                 database='attendance')

    cursor = conn.cursor()

    cursor.execute("SELECT roll_no, name, time FROM attendance WHERE date = %s", (formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    if not attendance_data:
        return render_template('attendance.html', selected_date=selected_date, no_data=True)
    
    return render_template('attendance.html', selected_date=selected_date, attendance_data=attendance_data)


if __name__ == '__main__':
    app.run(debug=True)
