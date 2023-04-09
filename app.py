import os
import pandas as pd
import numpy as np
import openpyxl
import psycopg2
import datetime
from datetime import date
from flask import Flask, request, redirect, url_for,flash,abort
from flask import render_template
from config import get_db_connection
from flask import make_response
from flask import abort
from flask import Flask
from flask import Flask
from flask_caching import Cache
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from config import pg_engine
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import login_user,login_required,logout_user
from flask_bootstrap import Bootstrap
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from datetime import date






UPLOAD_FOLDER=r"U:\\"


ALLOWED_EXTENSIONS = { 'csv','xlsx'}

app = Flask(__name__)

# Flask-Bootstrap requires this line
Bootstrap(app)

# Set the database URI using the PostgreSQL JDBC driver
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{user}:{psw}@localhost/{db}".format(user='postgres',psw='Privacy@100',db='school')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = 'fneapgfvnoowenvfbijnwgvopbi9wo'
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1000 * 100

@app.route('/',methods=("POST", "GET"))
def login():
      
    return render_template('login_page.html',)
  
@app.route('/signup',methods=("POST", "GET"))
def signup():
      
  return render_template('signup_page.html')
    
  
@app.route('/forgotpassword',methods=("POST", "GET"))
def forgotpassword():
    return render_template('forgotpassword.html')
    
@app.route('/home',methods=("POST", "GET"))
def home():
  user_name = request.form
# return render_template('Home_page.html')
  return user_name
    
#Student Info page
@app.route('/studentinfoCLASS',methods=("POST", "GET"))
def studentinfo():
    cl=request.form['class_info']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM student_details WHERE Current_Class={cl};''')
    db_tables=cur.fetchall()
    tables =[table for table in db_tables]
    cur.execute('''SELECT * FROM information_schema.columns WHERE table_schema = 'public'AND table_name   = 'student_details';''')
    col_name=[col[3] for col in cur.fetchall()]
    cur.close()
    conn.close()
    df=pd.DataFrame(data=tables,columns=col_name)
    return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)


#Student Marks page
@app.route('/marksnavigator',methods=("POST", "GET"))
def marksnavigator():
    
    return render_template('marks_naviagtion.html')

#Update marks
@app.route('/marks_data_entry', methods=['GET', 'POST'])
def marks_data_entry():
   
    cl=request.form['marks_update']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT roll_number, student_name FROM student_details where current_class = {cl};''')
    students = cur.fetchall() 
    # subjects=['English','Hindi','Telugu','Maths','Science','Social']
    students=[tuple(list(t) + ['English','Hindi','Telugu','Maths','Science','Social',]) for t in students]
    # return cl
    return render_template('marks_form.html', students=students,cls=cl)

# #Marks report
@app.route('/marks_data_change', methods=['GET', 'POST'])
def marks_data_change():
  exam_type=request.form['exam_type']
  marks_change_class=request.form['marks_change_class']
  conn = get_db_connection()
  #get table names from DB
  cur = conn.cursor()
  cur.execute(f'''SELECT DISTINCT roll_number from acadamic_reports WHERE current_class = {marks_change_class} AND exam_type='{exam_type}';''')
  students = [roll[0]for roll in cur.fetchall()] 
  cur.execute(f'''SELECT DISTINCT subject from acadamic_reports WHERE current_class = {marks_change_class} AND exam_type='{exam_type}';''')
  subject = [sub[0]for sub in cur.fetchall()] 
  # df=pd.DataFrame(data=students,columns=['roll_number','subject'])
  # df.groupby()
  return render_template('edit_marks.html',students=students,subject=subject,exam_type=exam_type,clss=marks_change_class)
  # return request.form
# #Marks report
@app.route('/marks_data_change_entry', methods=['GET', 'POST'])
def marks_data_change_entry():
  lc_pg_eng=pg_engine()
  conn = get_db_connection()
  records=request.form.to_dict()
  df=pd.DataFrame()
  df['roll_number']=[records.get('roll_number')]
  df['subject']=[records.get('subject')]
  df['score']=[records.get('score')]
  df['current_class']=[records.get('cls')]
  df['exam_type']=[records.get('exam_type')]
  cur = conn.cursor()
  cur.execute(f'''UPDATE acadamic_reports    
              SET score = {records.get('score')}
              WHERE
              roll_number={records.get('roll_number')} AND current_class= {records.get('cls')} AND 
              subject= '{records.get('subject')}' AND exam_type= '{records.get('exam_type')}'; ''')
  conn.commit()
  conn.close()
  return render_template("sucessfully_updated.html")
  # return request.form

#Marks report
@app.route('/marks_data', methods=['GET', 'POST'])
def marks_data():
    lc_pg_eng=pg_engine()
    conn = get_db_connection()
    marks_records=request.form.to_dict()
    cls=request.form['cls']
    exam_type=request.form['exam_type']
    marks_records.pop('cls')
    marks_records.pop('exam_type')
    roll_number=[i.split("-")[0] for i in marks_records.keys()]
    subject=[i.split("-")[1] for i in marks_records.keys()]
    score=marks_records.values()

    df=pd.DataFrame()
    df['roll_number']=roll_number
    df['subject']=subject
    df['score']=score
    df['current_class']=cls
    df['exam_type']=exam_type
    
    df.to_sql('acadamic_reports',con=lc_pg_eng,if_exists='append',index=False)
    
    return render_template("sucessfully_updated.html")
#View Marks 
@app.route('/marksinfoCLASS',methods=("POST", "GET"))
def marksinfo():
    exam_type=request.form['exam_type']
    cl=request.form['marks_info']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM acadamic_reports where current_class = {cl} AND exam_type= '{exam_type}';''')
    db_tables=cur.fetchall()
    tables =[table for table in db_tables]
    cur.execute('''SELECT * FROM information_schema.columns WHERE table_schema = 'public'AND table_name   = 'acadamic_reports';''')
    col_name=[col[3] for col in cur.fetchall()]
    cur.execute(f'''SELECT roll_number,student_name FROM student_details where current_class = {cl} ;''')
    student_names=cur.fetchall()
    student_info =[std_info for std_info in student_names]
    std_info=pd.DataFrame(data=student_info,columns=['roll_number','student_name'])
    df=pd.DataFrame(data=tables,columns=col_name)
    df=df.merge(std_info,how='inner',on='roll_number')
    marks_list=pd.pivot_table(df,index=['roll_number','student_name'],columns=['subject'],values='score')
    marks_list['Total_score']=marks_list.sum(axis=1)
    marks_list['percentage']=pd.pivot_table(df,index=['roll_number','student_name'],columns=['subject'],values='score').sum(axis=1)/df['subject'].nunique()
    marks_list=marks_list.sort_values(by='percentage',ascending=False).reset_index()
    # return exam_type
    return render_template('simple.html',  tables=[marks_list.to_html(classes='data')], titles=marks_list.columns.values,exam_type=exam_type)

@app.route('/view_attentence_fillter',methods=("POST", "GET"))
def attentence_fillter_date():
  
  return render_template('attendance_navigation.html')
 
@app.route('/attentence_info',methods=("POST", "GET"))
def attentence_info():
  
  return render_template("view_attentence_fillters.html")

@app.route('/attendence_report',methods=("POST", "GET"))
def attendence_report():
  cl=request.form['attendence_class']
  start_date = str(request.form['from_date'])
  end_date = str(request.form['to_date'])
  conn = get_db_connection()
  #get table names from DB
  cur = conn.cursor()
  cur.execute(f'''SELECT * FROM attendence WHERE Current_Class={cl};''')
  db_tables=cur.fetchall()
  tables =[table for table in db_tables]
  cur.execute('''SELECT * FROM information_schema.columns WHERE table_schema = 'public'
              AND table_name   = 'attendence';''')
  col_name=[col[3] for col in cur.fetchall()]
  cur.close()
  conn.close()
  df=pd.DataFrame(data=tables,columns=col_name)
  df['date']= pd.to_datetime(df['date'])
  df=df.loc[(df['date']>=start_date) & (df['date']<=end_date)]
  attendes_df=pd.pivot_table(data=df,values='attendance',index=['roll_number', 'student_name', 'current_class'],columns=df['date'].dt.date)
  attendes_df['attendence_pecent']=(attendes_df.sum(axis=1)/len(attendes_df.columns))*100
  attendes_df['Prestent_days']=attendes_df[attendes_df.columns[:-1]].sum(axis=1)
  Total_attendence=attendes_df.pop('Prestent_days')
  attendence_percentage=attendes_df.pop('attendence_pecent')
  attendes_df.insert(0,"Attendence_percentage",attendence_percentage)
  attendes_df.insert(1,"Prestent_days",Total_attendence)
  attendes_df=attendes_df.reset_index()
  return render_template('simple.html',  tables=[attendes_df.to_html(classes='data')], titles=attendes_df.columns.values)

@app.route('/attentence_rcrd',methods=("POST", "GET"))
def attentence_rcrd():
  
  return render_template("attendance_rcrd.html")

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    dt=request.form['Date']
    cl=request.form['attendence_class']
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT roll_number, student_name FROM student_details where current_class = {cl};''')
    students = cur.fetchall()
    students=[tuple(list(t) + [dt,cl]) for t in students]
    # Display form
    return render_template('attendence_form.html', students=students,cls=cl,Date=dt)
@app.route('/attendance_data', methods=['GET', 'POST'])
def attendance_data():
    date =request.form['Date']
    cl=request.form['cls']
    df=pd.DataFrame()
    lc_pg_eng=pg_engine()
    attendance_record=request.form.to_dict()
    roll_numbers=attendance_record.keys()
    attendance=attendance_record.values()
    cls=attendance_record.pop('cls')
    date=attendance_record.pop('Date')
    df=pd.DataFrame()
    df['roll_number']=roll_numbers
    df['attendance']=attendance
    df['date']=date
    df['current_class']=cls
    conn = get_db_connection()
    #get table names from DB
    cur = conn.cursor()
    cur.execute(f'''SELECT roll_number, student_name FROM student_details where current_class = {cl};''')   
    db_tables=cur.fetchall()
    tables =[table for table in db_tables]
    col_name=['roll_number','student_name']
    dbdf=pd.DataFrame(data=tables,columns=col_name)
    dbdf['roll_number']=dbdf['roll_number'].astype(str)
    df=pd.merge(left=dbdf,right=df,how='inner',on=['roll_number'])  
    df=df[['roll_number','student_name','current_class','date','attendance']]
    df.to_sql('attendence',con=lc_pg_eng,if_exists='append',index=False)
    return redirect("/attentence_info")
  
if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True,host='10.80.1.72',port=2545)