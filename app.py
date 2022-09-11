from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user

#from flask_mail import Mail


import json
import numpy as np
import pickle
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objs as go





model = pickle.load(open('stresslevel.pkl', 'rb'))
#creation of the Flask Application named as "app"
# mydatabase connection
local_server=True
app=Flask(__name__)


app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

# app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/mental'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)
app.secret_key="tandrima"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    usn=db.Column(db.String(20),unique=True)
    pas=db.Column(db.String(1000))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        usn=request.form.get('usn')
        pas=request.form.get('pas')
        
        # print(usn,pas)
        encpassword=generate_password_hash(pas)
        user=User.query.filter_by(usn=usn).first()
        if user:
            flash("UserID is already taken","warning")
            return render_template("usersignup.html")
            
        db.engine.execute(f"INSERT INTO `user` (`usn`,`pas`) VALUES ('{usn}','{encpassword}') ")
                
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")        

    return render_template("usersignup.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        usn=request.form.get('usn')
        pas=request.form.get('pas')
        user=User.query.filter_by(usn=usn).first()
        if user and check_password_hash(user.pas,pas):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))


@app.route('/music')
@login_required
def music():
    return render_template('music.html')


@app.route('/quizandgame')
@login_required
def quizandgame():
    return render_template('quizandgame.html')

    
@app.route('/exercises')
@login_required
def exercises():
    return render_template('exercises.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/game')
def game():
    return render_template('game.html')


@app.route('/analysis',methods=['GET'])
def analysis():
     #reading the dataset
    train_df = pd.read_csv('dreaddit-train.csv',encoding='ISO-8859-1')
    train_df.drop(['text', 'post_id' , 'sentence_range', 'id', 'social_timestamp'], axis=1, inplace=True)
    values = train_df['subreddit'].value_counts()
    labels = train_df['subreddit'].value_counts().index

    fig = px.pie(train_df, names=labels, values=values)
    fig.update_layout(title='Distribution of Subreddits')
    fig.update_traces(hovertemplate='%{label}: %{value}')
    #convert the plot to JSON using json.dumps() and the JSON encoder that comes with Plotly
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    train_df['label'].replace([0,1],['Not in Stress','In Stress'],inplace=True)
    fig2=px.histogram(train_df,
                 x="label",
                
                 title='Distribution of Stress Type',
                 color="label"
    )
    fig2.update_layout(bargap=0.1)
    #convert the plot to JSON using json.dumps() and the JSON encoder that comes with Plotly
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    fig3 = px.bar(train_df,
                 x='subreddit',
                 y='sentiment',
                 title='Car brand year resale ratio',
             color='subreddit')
    fig3.update_traces()
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    fig4 = px.scatter(train_df,
                 x='subreddit',
                 y='social_karma',
                 title='Car brand price thousand ratio',
                 color="subreddit")
    fig4.update_traces()
    graphJSON4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    
    fig5 = px.histogram(train_df,
                   x='confidence',
                   marginal='box',
                   title='Distribution of count reason of Mental Health issue',)
    fig5.update_layout(bargap=0.1)
    graphJSON5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    
    fig6=px.histogram(train_df,
                 x="subreddit",
                
                 title='Distribution of Vehicle Type',color='subreddit')
    fig6.update_layout(bargap=0.1)
    graphJSON6 = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('analysis.html', graphJSON=graphJSON,graphJSON2=graphJSON2,graphJSON3=graphJSON3,graphJSON4=graphJSON4,
                           graphJSON5=graphJSON5,graphJSON6=graphJSON6)
   

@app.route('/i')
def i():
    return render_template('stress.html')



@app.route('/stressdetect',methods=['POST'])
def stressdetect():
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)
    #on basis of prediction displaying the desired output
    if prediction=="Absence":
        data="You are having Normal Stress!! Take Care of yourself"
    elif prediction=="Presence":
        data="You are having High Stress!! Consult a doctor and get the helpline number from our chatbot"
    return render_template('stress.html', prediction_text3='Stress Level is: {}'.format(data))





if __name__=="__main__":
    app.run(debug=True)