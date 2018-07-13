from flask import Flask, render_template, send_from_directory, jsonify, request
from datetime import datetime, timedelta
import json, jwt
from utils.mailgun import Mailgun

import firebase_admin
from firebase_admin import credentials, auth
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

config = {}
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

app = Flask(__name__, template_folder='templates/html')
mailgun = Mailgun(api_key = config['mailgun-api-key'], domain_name = config['mailgun-domain-name'])

def _send_verification_email(uid, email):
    token = jwt.encode({
            'uid': uid, 
            'exp': datetime.utcnow() + timedelta(days = config['verification-token-lifetime-hours']),
        }, config['jwt-secret'], algorithm='HS256').decode("utf-8")

    url = "{base_url}auth/verify?token={token}".format(base_url = config['application-base-url'], token = token)
    email_body = ""
    email_subject = config['verification-email-subject']
    with open('./templates/email/verification.txt') as email_template_file:
        email_body = email_template_file.read().format(url = url)
    
    email_body = email_body.format(url = url)
    sent_success = mailgun.send_single_email(from_email_account = config['email-account-name'], 
                            from_name = '', 
                            to_email = email, 
                            to_name = '', 
                            subject = email_subject, 
                            body = email_body)

    return sent_success

def _send_password_reset_email(uid, email):
    token = jwt.encode({
            'uid': uid, 
            'exp': datetime.utcnow() + timedelta(hours = config['password-reset-token-lifetime-hours']),
        }, config['jwt-secret'], algorithm='HS256').decode("utf-8")

    url = "{base_url}auth/reset_password?token={token}".format(base_url = config['application-base-url'], token = token)
    email_body = ""
    email_subject = config['password-reset-email-subject']
    with open('./templates/email/password_reset.txt') as email_template_file:
        email_body = email_template_file.read().format(url = url)
    
    email_body = email_body.format(url = url)
    sent_success = mailgun.send_single_email(from_email_account = config['email-account-name'], 
                            from_name = '', 
                            to_email = email, 
                            to_name = '', 
                            subject = email_subject, 
                            body = email_body)

    return sent_success



@app.route('/api/auth/send_verification', methods=["POST"])
def send_verification_email():
    json_data = request.get_json()
    if not json_data or not json_data['token']:
        return jsonify({
            'success': 0,
            'msg': 'invalid token'
        }), 403

    decoded_token = auth.verify_id_token(json_data['token'])
    uid = decoded_token['uid']
    user = auth.get_user(uid)

    if user.email_verified:
        return jsonify({
            'success': 0,
            'msg': 'already verified'
        }), 400
    
    sent_success = _send_verification_email(uid = uid, email = user.email)

    if sent_success:
        return jsonify({
            'success': 1,
            'msg': 'verification email sent'
        })
    else: 
        return jsonify({
            'success': 1,
            'msg': 'internal error'
        }), 500


@app.route('/api/auth/send_password_reset', methods = ['POST'])
def send_reset_password():
    json_data = request.get_json()
    if not json_data or not json_data['email']:
        return jsonify({
            'success': 0,
            'msg': 'missing email'
        }), 400
    email = json_data['email']
    try:
        user = auth.get_user_by_email(email)
    except:
        return jsonify({
            'success': 0,
            'msg': 'user not found'
        }), 400
    
    sent_success = _send_password_reset_email(uid = user.uid, email = email)
    
    if sent_success:
        return jsonify({
            'success': 1,
            'msg': 'password reset email sent'
        })
    else: 
        return jsonify({
            'success': 1,
            'msg': 'internal error'
        }), 500


@app.route('/api/auth/reset_password', methods = ['PATCH'])
def reset_password():
    json_data = request.get_json()
    if not (json_data and json_data['password'] and json_data['token']):
        return jsonify({
            'success': 0,
            'msg': 'data missing'
        }), 400

    try:
        payload = jwt.decode(json_data['token'], config['jwt-secret'], algorithms=['HS256'])
        uid = payload['uid']
    except jwt.exceptions.ExpiredSignatureError:
        return jsonify({
            'success': 0,
            'msg': 'token expired'
        }), 400
    except:
        return jsonify({
            'success': 0,
            'msg': 'token invalid'
        }), 400
    try:
        auth.update_user(uid, password = json_data['password'], email_verified = True)
    except Exception as e:
        return jsonify({
            'success': 0,
            'msg': str(e)
        }), 400
    
    return jsonify({
        'success': 1,
        'msg': 'password updated'
    }), 200

@app.route('/')
def index_page():
    firebase_config = {key: config[key] for key in [
                                    'firebase-apiKey', 
                                    'firebase-authDomain',
                                    'firebase-databaseURL',
                                    'firebase-projectId',
                                    'firebase-storageBucket',
                                    'firebase-messagingSenderId',
                                    ]}
    return render_template('index.html', base_url = config['application-base-url'], firebase_config = firebase_config)

@app.route('/auth/reset_password')
def reset_password_page():
    token = request.args.get('token')
    if not token:
        msg = 'token missing'
        return render_template('password_reset_error.html', error = msg)
    try:
        payload = jwt.decode(token, config['jwt-secret'], algorithms=['HS256'])
        uid = payload['uid']
    except jwt.exceptions.ExpiredSignatureError:
        msg = 'token expired'
        return render_template('password_reset_error.html', error = msg)
    except:
        msg = 'token invalid'
        return render_template('password_reset_error.html', error = msg)

    user = auth.get_user(uid)

    return render_template('password_reset.html', email = user.email, token = token, base_url = config['application-base-url'])

@app.route('/auth/verify')
def verify_page():
    token = request.args.get('token')
    msg = ''
    try:
        payload = jwt.decode(token, config['jwt-secret'], algorithms=['HS256'])
        uid = payload['uid']
        auth.update_user(uid, email_verified = True)
        msg = 'verification success'
    except jwt.exceptions.ExpiredSignatureError:
        msg = 'token expired'
    except:
        msg = 'token invalid'
    return render_template('verification.html', msg = msg)

# NOTE: The preferred method is to use nginx or another web server to serve static files
@app.route('/static/<path>')
def static_file(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug = True)
