from flask import Flask,render_template,request,redirect,url_for,session,g
from new import final_summary_url
from neww import final_summary_text
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from definition import definition_word
import sqlite3
import urllib.request
import re
import os
import smtplib
import vlc, pafy
from flask_mail import Mail,Message
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///login.db'
#initialize the database

conn=sqlite3.connect('notes.db')
c=conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS saved_notes(user TEXT , title TEXT , notes TEXT , time_created VARCHAR )")
conn.commit()
conn.close()

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your email here'
app.config['MAIL_PASSWORD'] = 'your password here'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'your email here'
app.config['MAIL_ASCII_ATTACHMENTS'] = True 
app.config['DEBUG'] = True
app.secret_key="your secret key here"

mail=Mail(app)
#os.add_dll_directory(os.getcwd())



@app.route('/')
def homepage():
    return render_template('login.html')

@app.route('/edudot_login')
def edudot_login():
    if g.user:
        return redirect(url_for('display_edudot_first'))
    else:
        return redirect(url_for('homepage'))

@app.route('/display_edudot_first')
def display_edudot_first():
    if g.user:
        return render_template('edudot.html',name=session['user'])
    else:
        return render_template('login.html',error="Login before using services.")

@app.route('/display_edudot')
def display():
    if g.user:
        return render_template('edudot.html')
    else:
        return render_template("login.html",error="Login before using services.")

@app.route('/login_data' , methods=['GET','POST'])
def login():
    if request.method=="POST":
        session.pop('user',None)
        emil=request.form['email']
        pswrd=request.form['password']

        conn=sqlite3.connect('login.db')
        c=conn.cursor()
        c.execute("SELECT * from logindata WHERE email ='"+emil+"' ")
        r=c.fetchall()
        if len(r) == 0:
            return render_template('login.html',error="Register before logging in.")
        conn.commit()
        conn.close()
        
        conn=sqlite3.connect('login.db')
        c=conn.cursor()
        c.execute("SELECT * from logindata WHERE email ='"+emil+"' and passwrd='"+pswrd+"' ")
        r=c.fetchall()
        
        for i in r:
            if (emil==i[0] and pswrd==i[1]):
                session['user']=emil
                return redirect('/edudot_login')
        return render_template('login.html',error="Invalid username or password.")



           
    return render_template("login.html",error='{} method is get.'.format(g.user))

    
@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/signup_data',methods=["POST","GET"])
def signup_data():
    if request.method=="POST":
        namee=request.form['name']
        emaill=request.form['email']
        psword=request.form['password']
        cnfpsswrd=request.form['confirm_password']
        pnumber=request.form['phone']
        try:
            if namee=="" or emaill=="" or psword=="" or cnfpsswrd=="" or pnumber=="":
                return render_template('signup.html',error="Input fields cannot be left blank.")
            conn=sqlite3.connect('login.db')
            c=conn.cursor()
            c.execute("SELECT * FROM logindata WHERE email='"+emaill+"'")
            if c.fetchall():
                return render_template('signup.html',error="Email is already registered.")
            conn.commit()
            conn.close()
            if psword != cnfpsswrd:
                return render_template('signup.html',error="Passwords do not match")
        
            

            else:
                
                msg = Message('Welcome to Edudot', recipients = [emaill])
                msg.body = "Greetings {}!, you have successfully registered for Edudot(an online community of learners). Edudot provides exciting features and tools to aid your learning amidst these difficult times to make your learning fun and easy. Login into account and enjoy our free services. Happy Learning! ".format(namee)
                mail.send(msg)
                
                conn=sqlite3.connect('login.db')
                c=conn.cursor()
                c.execute("INSERT INTO logindata VALUES('"+emaill+"', '"+psword+"')")
                conn.commit()
                conn.close()
                return render_template('login.html',error="Your account is created, Login now to avail our services.")
        except:
            return render_template('signup.html',error="Enter a valid registered email.")

            
    return render_template("signup.html")

@app.route('/text_summ')
def edudot_summ():
    if g.user:
        return render_template('text_summary.html')
    else:
        return render_template('login.html',error="Login before using services.")

@app.route('/sum_url',methods=["POST","GET"])
def sum_url():
    if request.method=="POST":
        url=request.form['url']
        nos=request.form['nos']
        if nos=="":
            nos=10
        values=final_summary_url(url,int(nos))
        ans=values[0]
        org_text=values[1]
        return render_template('summary_print_url.html',summary_url=ans,org_text_url=org_text)
    else:
        return render_template('text_summary.html')

@app.route('/sum_text',methods=["POST","GET"])
def sum_text():
    if request.method == "POST":
        text=request.form['text']
        nos=request.form['nos']
        ans=final_summary_text(text,int(nos))
        return render_template('summary_print_text.html',summary_text=ans,org_text_text=text)
    else:
        return render_template('text_summary.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return render_template('login.html',error="Successfully logged out.")

@app.route('/make_notes')
def make_notes():
    if g.user :
        return render_template('notes.html')
    return render_template('login.html',error="Login before using services.")


@app.route('/save_notes',methods=['GET','POST'])
def save_notes():
    if request.method=="POST":
        if g.user == None:
            return render_template('login.html',error="Login before using services.")
        title=request.form['title']
        note=request.form['note']
        date=str(datetime.date(datetime.now()))
        conn=sqlite3.connect('notes.db')
        c=conn.cursor()
        c.execute("SELECT * FROM saved_notes WHERE user='"+g.user+"' and title='"+title+"' ")
        r=c.fetchall()
        if len(r):
            return render_template('notes.html',message="Notes are already saved with this title name,choose another title to save your notes.")
        else:
            #c=conn.cursor()
            listicle=[]
            listicle.append((g.user,title,note,date))
            conn.executemany("INSERT INTO saved_notes (user, title, notes, time_created) VALUES (?,?,?,?)", listicle)
            #c.execute("INSERT INTO saved_notes VALUES('"+g.user+"','"+title+"','"+note+"','"+str(datetime.date(datetime.now()))+"')")
            conn.commit()
            conn.close()
            return render_template('notes.html',message="Notes saved successfully.")  
    else:
        return render_template('notes.html')

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user=session['user']

@app.route('/view_saved_notes')
def view_saved_notes():
    if g.user:
        conn=sqlite3.connect('notes.db')
        c=conn.cursor()
        c.execute("SELECT * FROM saved_notes WHERE user='"+g.user+"'")
        r=c.fetchall()
        conn.commit()
        conn.close()
        return render_template('saved.html',lengt=len(r),notes=r)
    else:
        return render_template('login.html',error="Login before viewing your notes.")

@app.route('/delete/<string:title>')
def delete(title):
    if g.user:
        try:
            conn=sqlite3.connect('notes.db')
            c=conn.cursor()
            c.execute("DELETE FROM saved_notes WHERE user='"+g.user+"' AND title='"+title+"'")
            conn.commit()
            conn.close()
            
            conn=sqlite3.connect('notes.db')
            c=conn.cursor()
            c.execute("SELECT * FROM saved_notes WHERE user='"+g.user+"'")
            r=c.fetchall()
            conn.commit()
            conn.close()
            return redirect(url_for('view_saved_notes'))#('saved.html',lengt=len(r),notes=r)
        except:
            return render_template('notes.html',message="Unable to delete notes.")

            

    else:
        return render_template('Login before using our services.')

@app.route('/save_summary/<string:summary>',methods=["POST","GET"])
def save_summary(summary):
    if request.method=="POST":
        title=request.form['title']
        note=summary
        date=str(datetime.date(datetime.now()))
        conn=sqlite3.connect('notes.db')
        c=conn.cursor()
        c.execute("SELECT * FROM saved_notes WHERE title='"+title+"'")
        r=c.fetchall()
        conn.commit()
        conn.close()
        if len(r):
            return render_template('summary_print.html',error="Notes are already saved with this title. Kindly select a new title")
        conn=sqlite3.connect('notes.db')
        c=conn.cursor()
        listicle=[]
        listicle.append((g.user,title,note,date))
        conn.executemany("INSERT INTO saved_notes (user, title, notes, time_created) VALUES (?,?,?,?)", listicle)
        
        #c.executemany("INSERT INTO saved_notes VALUES('"+g.user+"','"+title+"','"+note+"','"+date+"')")
        conn.commit()
        conn.close()
        return render_template('text_summary.html')
        
    else:
        return render_template('text_summary.html')

@app.route('/search_saved_notes',methods=["GET","POST"])
def search_saved_notes():
    if g.user:

        if request.method=="POST":
            title=request.form['search']
            conn=sqlite3.connect('notes.db')
            c=conn.cursor()
            c.execute("SELECT * FROM saved_notes WHERE user = '"+g.user+"' AND title='"+title+"' ")
            r=c.fetchall()
            conn.commit()
            conn.close()
            if len(r):
                return render_template('saved.html',lengt=len(r),notes=r)
            else:
                return render_template('saved.html',lengt=0,error="No notes saved this name. ")
        else:
            return render_template('notes.html')
    else:
        return render_template('login.html',error="Login before using services.")

@app.route('/play_video',methods=["POST","GET"])
def play_video():
    if g.user:
        if request.method=="POST":
            video=request.form['video']
            #search_keyword=video
            
            search_keyword=video.replace(" ","+")
            html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            url="https://www.youtube.com/watch?v=" + video_ids[0]
            video = pafy.new(url)
            best = video.getbest()
            global media
            media=vlc.MediaPlayer()
            media = vlc.MediaPlayer(best.url)
            #if f==1:
                #return render_template('bored.html',error="Stop the media currently being played.")
            media.play()
            return render_template('bored.html')

        else:
            return render_template('edudot.html')
    else:
        return render_template('login.html',error="Login before using services.")

@app.route('/stop_video')
def stop_video():
    if g.user:
        media.stop()
        f=0
        return render_template('bored.html')
    else:
        return render_template('login.html',error="Login before using services.")

@app.route('/search_defn',methods=["GET","POST"])
def search_defn():
    if g.user:
        if request.method=="POST":
            word=request.form['def']
            ans=definition_word(word)
            return render_template('text_summary.html',defn=ans,word=word.upper())
        else:
            return render_template('text_summary.html')

    else:
        return render_template('login.html',error="Login before using services.")

@app.route('/bored')
def bored():
    if g.user:
        return render_template('bored.html')
    else:
        return render_template('login.html',error="Login before using services.")

if __name__ == "__main__":
    app.run(debug=True)