from flask import Flask, render_template, url_for, request, redirect
import csv
import smtplib
from email.message import EmailMessage
from pathlib import Path

app = Flask(__name__)


@app.route('/')
def my_home():
    return render_template('index.html')


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


'''
def write_to_file(data):
    with open('database.txt', mode='a') as database:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        file = database.write(f'\n\n{email}, {subject}, {message}')


def write_to_csv(data):
    with open('database.csv', mode='a', newline='') as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database2, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message])
'''


def email_to_recipient(data):
    email = EmailMessage()
    email['to'] = 'jordinkolman@gmail.com'
    email['from'] = data['email']
    email['subject'] = data['subject']
    email.set_content(data['message'])

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('jordinkolmanportfoliosite@gmail.com', 'devsite123')
        smtp.send_message(email)


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            email_to_recipient(data)
            return redirect('/thankyou.html')
        except:
            return 'Email did not send. Please try again.'
    else:
        return 'Something went wrong. Please try again.'
