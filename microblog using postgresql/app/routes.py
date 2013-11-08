from flask import *
from functools import wraps
from flask import Flask, render_template, request
from forms import ContactForm
from time import *
import db
import psycopg2  

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'bozz'  

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('log'))
    return wrap

@app.route('/')
def welcome():
    return render_template('welcome.html')
  
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm() 
    if request.method == 'POST':
        return 'Mail send.'
    elif request.method == 'GET':
        return render_template('contact.html', form=form) 

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect (url_for('log'))

@app.route('/log', methods=['GET', 'POST'])
def log():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'mani' or request.form['password'] != '123':
            error = "Invalid Entry. Please try again with Username 'mani' and Password '123'"
        else:
            session['logged_in'] = True
            return redirect(url_for('post'))
    return render_template('log.html', error=error)

@app.route('/post')
@login_required
def post():
	return render_template('post.html')

@app.route('/post',methods=['POST'])
def add_post():
    conn=psycopg2.connect(database='manimkv')
    temp=conn.cursor()
    temp.execute("INSERT INTO blogspot (author,post,day,time) VALUES (%s,%s,%s,%s)",[request.form['title'],request.form['blogpost'],strftime("%d %b %Y ", gmtime()),strftime("%H:%M:%S ", gmtime())])
    conn.commit()
    temp.close()
    conn.close()
    return render_template('post.html')

@app.route('/blog')
def blog():
    conn=psycopg2.connect(database='manimkv')
    temp=conn.cursor()
    temp.execute("SELECT * FROM blogspot ORDER BY id desc")
    posts=[dict(id=i[0],author=i[1],post=i[2],day=i[3],time=i[4],comment=i[5]) for i in temp.fetchall()]	
    conn.commit()
    conn.close()
    if not posts:
	return render_template('blog.html')
    else:
	return render_template('blog.html',posts=posts)
		
@app.route('/blog',methods=['POST'])
def add_comment():
    p=int(request.form['postid'])
    conn=psycopg2.connect(database='manimkv')
    temp=conn.cursor()
    temp.execute("SELECT comment FROM blogspot WHERE id=(%s)",[p])
    comments=[temp.fetchall()]	
    if comments[0][0][0]==None:
	temp.execute("UPDATE blogspot SET comment=(%s) WHERE id=(%s)",['\n@'+request.form['guest']+ '  says: \n'+request.form['comments']+'\n',p])
    else:
	temp.execute("UPDATE blogspot SET comment=(%s) WHERE id=(%s)",['\n@'+request.form['guest']+ '  says: \n'+request.form['comments']+'\n'+comments[0][0][0]+'\n',p])
    temp.execute("SELECT * FROM blogspot ORDER BY id desc")
    posts=[dict(id=i[0],author=i[1],post=i[2],day=i[3],time=i[4],comment=i[5]) for i in temp.fetchall()]	
    conn.commit()
    conn.close()
    if not posts:
	return render_template('blog.html')
    else:
	return render_template('blog.html',posts=posts)

if __name__ == '__main__':
    app.run(debug=True)

