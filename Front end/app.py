from flask import Flask, render_template, request, redirect, url_for, session
import warnings
from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
import pickle as pkl
warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = 'stock'


model = load_model('models/Lstm_model.h5')


with open(file="models/scaler.pkl", mode="rb") as file:
    scaler = pkl.load(file=file)


def predict_label(old_value, new_value):
    input_data = []
    old = scaler.transform([[float(old_value)]])
    new = scaler.transform([[float(new_value)]])
    input_data.append(old[0][0])
    input_data.append(new[0][0])
    p = model.predict([input_data])
    print(p)
    result = scaler.inverse_transform(p)
    result = (result[0][0])
    print(result)
    return result


@app.route("/submit", methods=['GET', 'POST'])
def get_hours():
    if request.method == 'POST':
        old_value = request.form['past']
        new_value = request.form['new']
        p = predict_label(old_value, new_value)
        return render_template("home.html", predict=p)


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["password"]
        r1 = pd.read_excel('user.xlsx')
        for index, row in r1.iterrows():
            if row["email"] == str(email) and row["password"] == str(pwd):

                return redirect(url_for('home'))
        else:
            mesg = 'Invalid Login Try Again'
            return render_template('login.html', msg=mesg)
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['Email']
        password = request.form['Password']
        col_list = ["name", "email", "password"]
        r1 = pd.read_excel('user.xlsx', usecols=col_list)
        new_row = {'name': name, 'email': email, 'password': password}
        r1 = r1.append(new_row, ignore_index=True)
        r1.to_excel('user.xlsx', index=False)
        print("Records created successfully")
        # msg = 'Entered Mail ID Already Existed'
        msg = 'Registration Successfull !! U Can login Here !!!'
        return render_template('login.html', msg=msg)
    return render_template('register.html')


@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route('/password', methods=['POST', 'GET'])
def password():
    if request.method == 'POST':
        current_pass = request.form['current']
        new_pass = request.form['new']
        verify_pass = request.form['verify']
        r1 = pd.read_excel('user.xlsx')
        for index, row in r1.iterrows():
            if row["password"] == str(current_pass):
                if new_pass == verify_pass:
                    r1.replace(to_replace=current_pass, value=verify_pass, inplace=True)
                    r1.to_excel("user.xlsx", index=False)
                    msg1 = 'Password changed successfully'
                    return render_template('password_change.html', msg1=msg1)
                else:
                    msg2 = 'Re-entered password is not matched'
                    return render_template('password_change.html', msg2=msg2)
        else:
            msg3 = 'Incorrect password'
            return render_template('password_change.html', msg3=msg3)
    return render_template('password_change.html')


@app.route('/graphs', methods=['POST', 'GET'])
def graphs():
    return render_template('graphs.html')


@app.route('/lstm')
def lstm():
    return render_template('lstm.html')


@app.route('/arima')
def arima():
    return render_template('arima.html')


@app.route('/logout')
def logout():
    session.clear()
    msg='You are now logged out', 'success'
    return redirect(url_for('login', msg=msg))


if __name__ == '__main__':
    app.run(port=5002, debug=True)
